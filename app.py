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
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA

# Carregar e preparar os dados
file_path = 'BD_modelo.csv'
df = pd.read_csv(file_path)

# Codificar variáveis categóricas
label_encoder_pedra = LabelEncoder()
label_encoder_virada = LabelEncoder()

df['PEDRA'] = label_encoder_pedra.fit_transform(df['PEDRA'])
df['PONTO_VIRADA'] = label_encoder_virada.fit_transform(df['PONTO_VIRADA'])

# Separar as features e os targets
X = df[['ANO_INGRESSO', 'INDE', 'ano']]
y_pedra = df['PEDRA']
y_virada = df['PONTO_VIRADA']

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
st.title("Previsão de Pedra, Ponto de Virada e INDE para 2023 e 2024")

# Selecionar o ID_ALUNO
id_aluno = st.selectbox("Escolha o ID do Aluno", df['ID_ALUNO'].unique())

# Filtrar os dados do aluno selecionado
aluno_data = df[df['ID_ALUNO'] == id_aluno].sort_values(by='ano')

# Verificar se os dados do aluno estão disponíveis
if not aluno_data.empty:
    # Preparar os dados do aluno para previsões
    ano_ingresso = aluno_data['ANO_INGRESSO'].values[0]
    inde_series = aluno_data.set_index('ano')['INDE']

    # Ajustar o modelo ARIMA para prever INDE
    try:
        model = ARIMA(inde_series, order=(1, 1, 1))
        model_fit = model.fit()
        forecast = model_fit.forecast(steps=2)  # Prever 2023 e 2024

        # Previsões de INDE para 2023 e 2024
        inde_2023 = forecast.iloc[0]
        inde_2024 = forecast.iloc[1]
    except Exception as e:
        st.error(f"Erro ao gerar previsão ARIMA: {e}")
        inde_2023, inde_2024 = None, None

    # Fazer previsões para PEDRA e PONTO_VIRADA
    input_data = np.array([[ano_ingresso, inde_series.iloc[-1], 2023]])
    input_data_scaled = scaler.transform(input_data)

    pred_pedra = rf_pedra.predict(input_data_scaled)
    pred_virada = rf_virada.predict(input_data_scaled)

    # Traduzir a previsão de pedra para o valor original
    pedra_pred = label_encoder_pedra.inverse_transform(pred_pedra)

    # Mostrar acurácia dos modelos
    st.write(f"Acurácia do modelo para previsão de Pedra: {pedra_accuracy:.2f}")
    st.write(f"Acurácia do modelo para previsão de Ponto de Virada: {virada_accuracy:.2f}")

    # Exibir resultados
    st.write(f"**Previsão de Pedra para 2023**: {pedra_pred[0]}")
    st.write(f"**O aluno estará em ponto de virada em 2023**: {'Sim' if pred_virada[0] == 1 else 'Não'}")

    if inde_2023 is not None and inde_2024 is not None:
        # Plotar o gráfico de INDE de 2020 a 2024
        inde_history = inde_series.append(pd.Series([inde_2023, inde_2024], index=[2023, 2024]))

        st.write("### Evolução do INDE do aluno (2020-2024)")
        fig, ax = plt.subplots()
        inde_history.plot(ax=ax, marker='o', linestyle='-', color='b')

        # Adicionar valores no gráfico
        for i in inde_history.index:
            ax.text(i, inde_history.loc[i], f'{inde_history.loc[i]:.2f}', fontsize=12, ha='center')

        ax.set_title(f'Evolução do INDE do Aluno {id_aluno}')
        ax.set_ylabel('INDE')
        ax.set_xlabel('Ano')
        ax.set_xticks([2020, 2021, 2022, 2023, 2024])  # Exibir apenas os anos desejados
        ax.axvline(x=2023, color='r', linestyle='--', label='Previsão para 2023')
        ax.axvline(x=2024, color='orange', linestyle='--', label='Previsão para 2024')
        ax.legend()
        st.pyplot(fig)

else:
    st.write("Nenhum dado encontrado para o ID de aluno selecionado.")
