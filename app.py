# -*- coding: utf-8 -*-
"""Untitled5.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1n0nDYBSLwg1onTOtfKQvhqT4Ehcnb-_H
"""
import streamlit as st
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
import plotly.graph_objs as go
from sklearn.inspection import permutation_importance

# Carregar e preparar os dados
file_path = 'BD_modelo.csv'
df = pd.read_csv(file_path)

# Filtrar alunos que possuem dados suficientes para análise (exemplo: dados de 2022 e anteriores)
alunos_completos = df.groupby('ID_ALUNO').filter(lambda x: x['ano'].max() == 2022)

# Codificar variáveis categóricas
label_encoder_pedra = LabelEncoder()
label_encoder_virada = LabelEncoder()

alunos_completos['PEDRA'] = label_encoder_pedra.fit_transform(alunos_completos['PEDRA'])
alunos_completos['PONTO_VIRADA'] = label_encoder_virada.fit_transform(alunos_completos['PONTO_VIRADA'])

# Separar as features e os targets
X = alunos_completos[['ANO_INGRESSO', 'INDE', 'ano']]
y_pedra = alunos_completos['PEDRA']
y_virada = alunos_completos['PONTO_VIRADA']

# Dividir os dados para calcular acurácia
X_train, X_test, y_train_pedra, y_test_pedra = train_test_split(X, y_pedra, test_size=0.2, random_state=42)
_, _, y_train_virada, y_test_virada = train_test_split(X, y_virada, test_size=0.2, random_state=42)

# Padronizar as features
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Treinar os modelos para PEDRA e PONTO_VIRADA
rf_pedra = RandomForestClassifier(random_state=42)
rf_pedra.fit(X_train, y_train_pedra)

rf_virada = RandomForestClassifier(random_state=42)
rf_virada.fit(X_train, y_train_virada)

# Calcular acurácia dos modelos de PEDRA e PONTO_VIRADA
pedra_accuracy = accuracy_score(y_test_pedra, rf_pedra.predict(X_test))
virada_accuracy = accuracy_score(y_test_virada, rf_virada.predict(X_test))

# Criar interface no Streamlit
st.title("Previsão de Pedra, Ponto de Virada e INDE para 2023")

# Adicionar explicação sobre a acurácia
st.write("""
### Lógica de Acurácia
A acurácia apresentada para os modelos de previsão de Pedra e Ponto de Virada é baseada na proporção de previsões corretas que o modelo faz em comparação ao total de previsões. Para o modelo ARIMA de previsão de INDE, usamos a métrica de Erro Médio Quadrático Raiz (RMSE), que mede a diferença entre os valores previstos pelo modelo e os valores reais, indicando a precisão do modelo.
""")

# Destacar a escolha do ID do Aluno
st.markdown("## **Escolha o ID do Aluno**")
id_aluno = st.selectbox("", alunos_completos['ID_ALUNO'].unique())

# 3. Adicionar possibilidade de comparar múltiplos alunos
comparar_ids = st.multiselect("Selecione outros IDs de alunos para comparação", alunos_completos['ID_ALUNO'].unique(), default=[id_aluno])

# Filtrar os dados dos alunos selecionados
alunos_data = alunos_completos[alunos_completos['ID_ALUNO'].isin(comparar_ids)].sort_values(by='ano')

# 5. Verificar se os dados do aluno estão disponíveis
if not alunos_data.empty:
    for id_aluno in comparar_ids:
        aluno_data = alunos_data[alunos_data['ID_ALUNO'] == id_aluno]

        # Preparar os dados do aluno para previsões
        ano_ingresso = aluno_data['ANO_INGRESSO'].values[0]
        inde_series = aluno_data.set_index('ano')['INDE']

        # 6. Ajustar o modelo ARIMA para prever INDE
        try:
            model = ARIMA(inde_series, order=(1, 1, 1))
            model_fit = model.fit()
            forecast = model_fit.forecast(steps=1)  # Prever apenas 2023

            # Previsão de INDE para 2023
            inde_2023 = forecast.iloc[0]

            # Calcular erro (RMSE) do modelo ARIMA
            arima_rmse = np.sqrt(mean_squared_error(inde_series, model_fit.predict(start=inde_series.index[0], end=inde_series.index[-1])))

        except Exception as e:
            st.error(f"Erro ao gerar previsão ARIMA para o aluno {id_aluno}: {e}")
            inde_2023 = None
            arima_rmse = None

        # Fazer previsões para PEDRA e PONTO_VIRADA
        input_data = np.array([[ano_ingresso, inde_series.iloc[-1], 2023]])
        input_data_scaled = scaler.transform(input_data)

        pred_pedra = rf_pedra.predict(input_data_scaled)
        pred_virada = rf_virada.predict(input_data_scaled)

        # Traduzir a previsão de pedra para o valor original
        pedra_pred = label_encoder_pedra.inverse_transform(pred_pedra)

        # 7. Mostrar acurácia dos modelos com resultados grifados
        st.write(f"**Acurácia do modelo para previsão de Pedra (Aluno {id_aluno}):** **{pedra_accuracy:.2f}**")
        st.write(f"**Acurácia do modelo para previsão de Ponto de Virada (Aluno {id_aluno}):** **{virada_accuracy:.2f}**")
        if arima_rmse is not None:
            st.write(f"**Erro médio quadrático raiz (RMSE) do modelo ARIMA para INDE (Aluno {id_aluno}):** **{arima_rmse:.2f}**")

        # Exibir resultados grifados
        st.write(f"**Previsão de Pedra para 2023 (Aluno {id_aluno}):** **{pedra_pred[0]}**")
        st.write(f"**O aluno estará em ponto de virada em 2023 (Aluno {id_aluno}):** **{'Sim' if pred_virada[0] == 1 else 'Não'}**")

        if inde_2023 is not None:
            # Concatenação da previsão com a série existente
            inde_history = pd.concat([inde_series, pd.Series([inde_2023], index=[2023])])

            st.write(f"### Evolução do INDE do aluno {id_aluno} (2020-2023)")
            fig, ax = plt.subplots(figsize=(8, 4))  # Diminuir o tamanho do gráfico

            # 8. Plotar os anos até 2022 em azul
            ax.plot(inde_history.index[:len(inde_series)], inde_history.iloc[:len(inde_series)], marker='o', linestyle='-', color='blue')

            # Plotar a linha vermelha de 2022 para 2023
            ax.plot([2022, 2023], [inde_series.loc[2022], inde_2023], marker='o', linestyle='-', color='red')

            # Adicionar valores no gráfico
            for i in inde_history.index:
                ax.text(i, inde_history.loc[i], f'{inde_history.loc[i]:.2f}', fontsize=10, ha='center', color='white')  # Diminuir o tamanho da fonte

            # Configurar visual do gráfico
            ax.set_facecolor('#0E1117')
            fig.patch.set_facecolor('#0E1117')
            ax.set_title(f'Evolução do INDE do Aluno {id_aluno}', fontsize=14, color='white')  # Diminuir o tamanho da fonte do título
            ax.set_ylabel('INDE', fontsize=12, color='white')  # Diminuir o tamanho da fonte do rótulo
            ax.set_xlabel('Ano', fontsize=12, color='white')  # Diminuir o tamanho da fonte do rótulo
            ax.set_xticks([2020, 2021, 2022, 2023])  # Exibir apenas os anos desejados
            ax.tick_params(colors='white')
            ax.yaxis.set_visible(False)  # Remover números laterais
            ax.legend().set_visible(False)  # Remover a legenda
            st.pyplot(fig)

    # 9. Análise de Importância de Características
    st.write("### Importância das características no modelo RandomForest")
    importance_pedra = permutation_importance(rf_pedra, X_test, y_test_pedra, n_repeats=10, random_state=42)
    importance_virada = permutation_importance(rf_virada, X_test, y_test_virada, n_repeats=10, random_state=42)

    st.write(f"**Importância para PEDRA:** {dict(zip(X.columns, importance_pedra.importances_mean))}")
    st.write
