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

# Carregar as bases de dados
file_path_modelo = 'BD_modelo.csv'
file_path_final = 'BD_final.csv.csv'

df_modelo = pd.read_csv(file_path_modelo)
df_final = pd.read_csv(file_path_final, delimiter=';')

# Verificar as colunas disponíveis
st.write("Colunas disponíveis no BD_modelo:", df_modelo.columns)
st.write("Colunas disponíveis no BD_final:", df_final.columns)

# Filtrar alunos que possuem dados suficientes para análise (exemplo: dados de 2022 e anteriores)
alunos_completos = df_modelo.groupby('ID_ALUNO').filter(lambda x: x['ano'].max() == 2022)

# Adicionar a coluna de indicação de bolsa do df_final ao alunos_completos
df_final_relevante = df_final[['ID_ALUNO', 'INDICADO_BOLSA_2022']]
alunos_completos = pd.merge(alunos_completos, df_final_relevante, on='ID_ALUNO', how='left')

# Verificar se a coluna 'INDICADO_BOLSA_2022' existe
if 'INDICADO_BOLSA_2022' not in alunos_completos.columns:
    st.error("Coluna 'INDICADO_BOLSA_2022' não encontrada no DataFrame. Verifique o nome da coluna.")
else:
    # Codificar variáveis categóricas
    label_encoder_pedra = LabelEncoder()
    label_encoder_virada = LabelEncoder()
    label_encoder_bolsa = LabelEncoder()

    alunos_completos['PEDRA'] = label_encoder_pedra.fit_transform(alunos_completos['PEDRA'])
    alunos_completos['PONTO_VIRADA'] = label_encoder_virada.fit_transform(alunos_completos['PONTO_VIRADA'])
    alunos_completos['INDICADO_BOLSA_2022'] = label_encoder_bolsa.fit_transform(alunos_completos['INDICADO_BOLSA_2022'])

    # Separar as features e os targets
    X = alunos_completos[['ANO_INGRESSO', 'INDE', 'IAA', 'IEG', 'ano']]
    y_pedra = alunos_completos['PEDRA']
    y_virada = alunos_completos['PONTO_VIRADA']
    y_bolsa = alunos_completos['INDICADO_BOLSA_2022']

    # Dividir os dados para calcular acurácia
    X_train_pedra, X_test_pedra, y_train_pedra, y_test_pedra = train_test_split(X, y_pedra, test_size=0.2, random_state=42)
    X_train_virada, X_test_virada, y_train_virada, y_test_virada = train_test_split(X, y_virada, test_size=0.2, random_state=42)
    X_train_bolsa, X_test_bolsa, y_train_bolsa, y_test_bolsa = train_test_split(X, y_bolsa, test_size=0.2, random_state=42)

    # Padronizar as features
    scaler = StandardScaler()
    X_train_pedra = scaler.fit_transform(X_train_pedra)
    X_test_pedra = scaler.transform(X_test_pedra)
    X_train_virada = scaler.fit_transform(X_train_virada)
    X_test_virada = scaler.transform(X_test_virada)
    X_train_bolsa = scaler.fit_transform(X_train_bolsa)
    X_test_bolsa = scaler.transform(X_test_bolsa)

    # Treinar os modelos para PEDRA, PONTO_VIRADA e BOLSA
    rf_pedra = RandomForestClassifier(random_state=42)
    rf_pedra.fit(X_train_pedra, y_train_pedra)

    rf_virada = RandomForestClassifier(random_state=42)
    rf_virada.fit(X_train_virada, y_train_virada)

    rf_bolsa = RandomForestClassifier(random_state=42)
    rf_bolsa.fit(X_train_bolsa, y_train_bolsa)

    # Calcular acurácia dos modelos
    pedra_accuracy = accuracy_score(y_test_pedra, rf_pedra.predict(X_test_pedra))
    virada_accuracy = accuracy_score(y_test_virada, rf_virada.predict(X_test_virada))
    bolsa_accuracy = accuracy_score(y_test_bolsa, rf_bolsa.predict(X_test_bolsa))

    # Criar interface no Streamlit
    st.title("Previsão de Pedra, Ponto de Virada, Bolsa e INDE para 2023")

    # Adicionar explicação sobre a acurácia
    st.write("""
    ### Lógica de Acurácia
    A acurácia apresentada para os modelos de previsão de Pedra, Ponto de Virada e Bolsa é baseada na proporção de previsões corretas que o modelo faz em comparação ao total de previsões. Para o modelo ARIMA de previsão de INDE, usamos a métrica de Erro Médio Quadrático Raiz (RMSE), que mede a diferença entre os valores previstos pelo modelo e os valores reais, indicando a precisão do modelo.
    """)

    # 1. Análise Comparativa de Desempenho
    st.write("## Comparação entre Alunos Indicados para Bolsa e Não Indicados")
    bolsa_comparacao = alunos_completos.groupby('INDICADO_BOLSA_2022').agg({
        'INDE': 'mean',
        'IAA': 'mean',
        'IEG': 'mean'
    }).reset_index()

    st.write(bolsa_comparacao)

    # 3. Adicionar possibilidade de comparar múltiplos alunos
    comparar_ids = st.multiselect("Selecione IDs de alunos para comparação", alunos_completos['ID_ALUNO'].unique())

    # Filtrar os dados dos alunos selecionados
    alunos_data = alunos_completos[alunos_completos['ID_ALUNO'].isin(comparar_ids)].sort_values(by='ano')

    # 5. Verificar se os dados do aluno estão disponíveis
    if not alunos_data.empty:
        cols = st.columns(len(comparar_ids))  # Criar colunas para exibir gráficos lado a lado
        
        for index, id_aluno in enumerate(comparar_ids):
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

            # Fazer previsões para PEDRA, PONTO_VIRADA e BOLSA
            input_data = np.array([[ano_ingresso, inde_series.iloc[-1], aluno_data['IAA'].values[0], aluno_data['IEG'].values[0], 2023]])
            input_data_scaled = scaler.transform(input_data)

            pred_pedra = rf_pedra.predict(input_data_scaled)
            pred_virada = rf_virada.predict(input_data_scaled)
            pred_bolsa = rf_bolsa.predict(input_data_scaled)

            # Traduzir as previsões para os valores originais
            pedra_pred = label_encoder_pedra.inverse_transform(pred_pedra)
            bolsa_pred = label_encoder_bolsa.inverse_transform(pred_bolsa)

            with cols[index]:
                # 7. Mostrar acurácia dos modelos com resultados grifados
                st.write(f"**Aluno {id_aluno}:**")
                st.write(f"**Acurácia para previsão de Pedra:** **{pedra
                st.write(f"**Acurácia para previsão de Pedra:** **{pedra_accuracy:.2f}**")
                st.write(f"**Acurácia para previsão de Ponto de Virada:** **{virada_accuracy:.2f}**")
                st.write(f"**Acurácia para previsão de Bolsa:** **{bolsa_accuracy:.2f}**")
                if arima_rmse is not None:
                    st.write(f"**RMSE para INDE:** **{arima_rmse:.2f}**")

                # Exibir resultados grifados
                st.write(f"**Previsão de Pedra para 2023:** **{pedra_pred[0]}**")
                st.write(f"**Ponto de Virada em 2023:** **{'Sim' if pred_virada[0] == 1 else 'Não'}**")
                st.write(f"**Indicação para Bolsa em 2023:** **{'Sim' if bolsa_pred[0] == 1 else 'Não'}**")

                if inde_2023 is not None:
                    # Concatenação da previsão com a série existente
                    inde_history = pd.concat([inde_series, pd.Series([inde_2023], index=[2023])])

                    st.write(f"### Evolução do INDE (2020-2023)")
                    fig, ax = plt.subplots(figsize=(6, 3))  # Ajustar o tamanho do gráfico

                    # Plotar os anos até 2022 em azul
                    ax.plot(inde_history.index[:len(inde_series)], inde_history.iloc[:len(inde_series)], marker='o', linestyle='-', color='blue')

                    # Plotar a linha vermelha de 2022 para 2023
                    ax.plot([2022, 2023], [inde_series.loc[2022], inde_2023], marker='o', linestyle='-', color='red')

                    # Adicionar valores no gráfico
                    for i in inde_history.index:
                        ax.text(i, inde_history.loc[i], f'{inde_history.loc[i]:.2f}', fontsize=10, ha='center', color='white')

                    # Configurar visual do gráfico
                    ax.set_facecolor('#0E1117')
                    fig.patch.set_facecolor('#0E1117')
                    ax.set_title(f'Evolução do INDE do Aluno {id_aluno}', fontsize=14, color='white')
                    ax.set_ylabel('INDE', fontsize=12, color='white')
                    ax.set_xlabel('Ano', fontsize=12, color='white')
                    ax.set_xticks([2020, 2021, 2022, 2023])
                    ax.tick_params(colors='white')
                    ax.yaxis.set_visible(False)  # Remover números laterais
                    ax.legend().set_visible(False)  # Remover a legenda
                    st.pyplot(fig)

                    # 7. Alertas e Notificações
                    if inde_2023 < inde_series.mean():
                        st.warning(f"Alerta: Previsão de INDE para 2023 ({inde_2023:.2f}) está abaixo da média histórica ({inde_series.mean():.2f}) para o aluno {id_aluno}.")

# Adicionar explicação sobre a comparação de desempenho de bolsas
st.write("""
### Explicação sobre a Comparação de Desempenho
A tabela acima compara o desempenho médio de alunos indicados e não indicados para bolsa, utilizando variáveis como INDE, IAA e IEG. Essa análise permite entender melhor como essas métricas se relacionam com a probabilidade de um aluno ser indicado para bolsa.
""")

               
