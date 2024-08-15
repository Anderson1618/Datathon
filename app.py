# -*- coding: utf-8 -*-

"""
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
import plotly.express as px
import plotly.graph_objects as go
from statsmodels.tsa.arima.model import ARIMA

# ONG Passos Mágicos
st.title("ONG Passos Mágicos")
st.write("""
A **ONG Passos Mágicos** é uma organização dedicada a apoiar crianças e adolescentes em situação de vulnerabilidade, proporcionando-lhes oportunidades de desenvolvimento pessoal, educacional e profissional. Através de diversas atividades e programas, a ONG visa transformar vidas e construir um futuro mais promissor para os jovens que atende.

Este projeto, em colaboração entre FIAP e a  ONG, visa monitorar e prever indicadores acadêmicos cruciais, como o Índice de Desenvolvimento Educacional (INDE), a resiliência representada pela Pedra, e os pontos de virada, onde mudanças significativas no desempenho podem ocorrer. Essas projeções ajudam a identificar e intervir de forma mais eficaz na trajetória educacional dos alunos, garantindo que recebam o apoio necessário no momento certo.
""")

# Carga de dados
file_path = 'BD_modelo.csv'
df = pd.read_csv(file_path)

# Limpeza dos dados
alunos_completos = df.groupby('ID_ALUNO').filter(lambda x: x['ano'].max() == 2022)

# Codificação de variáveis categóricas
label_encoder_pedra = LabelEncoder()
label_encoder_virada = LabelEncoder()

alunos_completos['PEDRA'] = label_encoder_pedra.fit_transform(alunos_completos['PEDRA'])
alunos_completos['PONTO_VIRADA'] = label_encoder_virada.fit_transform(alunos_completos['PONTO_VIRADA'])

# Separando as features e os targets
X = alunos_completos[['ANO_INGRESSO', 'INDE', 'ano']]
y_pedra = alunos_completos['PEDRA']
y_virada = alunos_completos['PONTO_VIRADA']

# Dados divididos em treino e teste
X_train, X_test, y_train_pedra, y_test_pedra = train_test_split(X, y_pedra, test_size=0.2, random_state=42)
_, _, y_train_virada, y_test_virada = train_test_split(X, y_virada, test_size=0.2, random_state=42)

# Padronização
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Treino dos modelos
rf_pedra = RandomForestClassifier(random_state=42)
rf_pedra.fit(X_train, y_train_pedra)

rf_virada = RandomForestClassifier(random_state=42)
rf_virada.fit(X_train, y_train_virada)

# Calculo de acurácia dos modelos de PEDRA e PONTO_VIRADA
pedra_accuracy = accuracy_score(y_test_pedra, rf_pedra.predict(X_test))
virada_accuracy = accuracy_score(y_test_virada, rf_virada.predict(X_test))

# Interface Streamlit
st.title("Projeção de Pedra, Ponto de Virada e INDE para 2023")

# Análise Comparativa de Alunos
st.write("## Análise Comparativa de Múltiplos Alunos")
comparar_ids = st.multiselect("Selecione IDs de alunos para comparação", alunos_completos['ID_ALUNO'].unique())

alunos_data = alunos_completos[alunos_completos['ID_ALUNO'].isin(comparar_ids)].sort_values(by='ano')

# Gráficos
if not alunos_data.empty:
    st.write("## Tendência do INDE ao longo do tempo para Alunos Selecionados")
    fig = px.line(alunos_data, x='ano', y='INDE', color='ID_ALUNO', markers=True)
    st.plotly_chart(fig)

    st.write("---")

    st.write("## Correlação entre INDE, PEDRA, e PONTO_VIRADA")
    correlation = alunos_completos[['INDE', 'PEDRA', 'PONTO_VIRADA']].corr()
    fig_corr = go.Figure(data=go.Heatmap(
        z=correlation.values,
        x=correlation.columns,
        y=correlation.columns,
        colorscale='Blues'  # Ajuste de cor para combinar com os gráficos de linhas
    ))
    fig_corr.update_layout(title='Mapa de Calor das Correlações', xaxis_nticks=36)
    st.plotly_chart(fig_corr)

    st.write("---")

    cols = st.columns(len(comparar_ids))  # Criar colunas para exibir gráficos lado a lado

    for index, id_aluno in enumerate(comparar_ids):
        aluno_data = alunos_data[alunos_data['ID_ALUNO'] == id_aluno]

        # Preparar os dados do aluno para projeções
        inde_series = aluno_data.set_index('ano')['INDE']

        # Ajustar o modelo ARIMA para projetar INDE
        try:
            model = ARIMA(inde_series, order=(1, 1, 1))
            model_fit = model.fit()
            forecast = model_fit.forecast(steps=1)  # Projetar apenas 2023

            # Projeção de INDE para 2023
            inde_2023 = forecast.iloc[0]

            # Erro (RMSE) do modelo ARIMA
            arima_rmse = np.sqrt(mean_squared_error(inde_series, model_fit.predict(start=inde_series.index[0], end=inde_series.index[-1])))

        except Exception as e:
            st.error(f"Erro ao gerar projeção ARIMA para o aluno {id_aluno}: {e}")
            inde_2023 = None
            arima_rmse = None

        # Fazer projeções para PEDRA e PONTO_VIRADA
        input_data = np.array([[aluno_data['ANO_INGRESSO'].values[0], inde_series.iloc[-1], 2023]])
        input_data_scaled = scaler.transform(input_data)

        pred_pedra = rf_pedra.predict(input_data_scaled)
        pred_virada = rf_virada.predict(input_data_scaled)

        # Traduzir a projeção de pedra para o valor original
        pedra_pred = label_encoder_pedra.inverse_transform(pred_pedra)

        with cols[index]:
            st.write(f"**Aluno {id_aluno}:**")

            st.write(f"**Projeção de Pedra para 2023:** **{pedra_pred[0]}**")
            st.write(f"**Ponto de Virada em 2023:** **{'Sim' if pred_virada[0] == 1 else 'Não'}**")

            if inde_2023 is not None:
                # Concatenação da projeção com a série existente
                inde_history = pd.concat([inde_series, pd.Series([inde_2023], index=[2023])])

                fig = go.Figure()

                # Adicionar a série histórica de INDE
                fig.add_trace(go.Scatter(x=inde_series.index, y=inde_series, mode='lines+markers', name='Histórico INDE'))

                # Adicionar a projeção para 2023
                fig.add_trace(go.Scatter(x=[2022, 2023], y=[inde_series.iloc[-1], inde_2023],
                                         mode='lines+markers', name='Projeção 2023', line=dict(color='red')))

                fig.update_layout(xaxis_title='Ano',
                                  yaxis_title='INDE',
                                  height=400)  # Aumentar o tamanho do gráfico

                st.plotly_chart(fig)

    st.write("---")

# Simulação de Cenários
st.write("## Simulação de Cenários")
sim_id = st.selectbox("Selecione o ID do Aluno para Simulação", alunos_completos['ID_ALUNO'].unique())
sim_inde = st.number_input("Projeção de INDE para 2023 (Simulação)", value=5.0, min_value=0.0, max_value=10.0)

# Entrada de dados simulados
input_simulation = np.array([[alunos_completos.loc[alunos_completos['ID_ALUNO'] == sim_id, 'ANO_INGRESSO'].values[0], sim_inde, 2023]])
input_simulation_scaled = scaler.transform(input_simulation)

# Projeções com os dados simulados
sim_pred_pedra = rf_pedra.predict(input_simulation_scaled)
sim_pred_virada = rf_virada.predict(input_simulation_scaled)
sim_pedra_pred = label_encoder_pedra.inverse_transform(sim_pred_pedra)
st.write(f"**Projeção Simulada de Pedra para 2023:** **{sim_pedra_pred[0]}**")
st.write(f"**Ponto de Virada em 2023 (Simulado):** **{'Sim' if sim_pred_virada[0] == 1 else 'Não'}**")

st.write("---")

# Lógica de Acurácia e Métricas
st.write("## Lógica de Acurácia e Métricas")
st.write("""
A acurácia apresentada para os modelos de projeção de Pedra e Ponto de Virada é baseada nas projeções corretas feitas pelo modelo em comparação ao total de projeções.
Para o modelo ARIMA de projeção de INDE, usamos a métrica de Erro Médio Quadrático Raiz (RMSE), que mede a diferença entre os valores projetados pelo modelo e os valores reais, indicando a precisão do modelo.
""")

st.write(f"**Acurácia para projeção de Pedra:** **{pedra_accuracy:.2f}**")
st.write(f"**Acurácia para projeção de Ponto de Virada:** **{virada_accuracy:.2f}**")

if 'arima_rmse' in locals() and arima_rmse is not None:
    st.write(f"**RMSE para projeção de INDE:** **{arima_rmse:.2f}**")

st.write("---")

# Dados brutos (para análise detalhada)
if st.checkbox("Mostrar dados brutos dos alunos"):
    st.write(alunos_completos)



