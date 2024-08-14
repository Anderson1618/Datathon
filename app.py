# -*- coding: utf-8 -*-
"""Untitled5.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1n0nDYBSLwg1onTOtfKQvhqT4Ehcnb-_H
"""

import streamlit as st
import pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt

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
y_inde = df['INDE']

# Dividir os dados para calcular acurácia
X_train, X_test, y_train_pedra, y_test_pedra = train_test_split(X, y_pedra, test_size=0.2, random_state=42)
_, _, y_train_virada, y_test_virada = train_test_split(X, y_virada, test_size=0.2, random_state=42)
_, _, y_train_inde, y_test_inde = train_test_split(X, y_inde, test_size=0.2, random_state=42)

# Padronizar as features
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Treinar os modelos
rf_pedra = RandomForestClassifier(random_state=42)
rf_pedra.fit(X_train, y_train_pedra)

rf_virada = RandomForestClassifier(random_state=42)
rf_virada.fit(X_train, y_train_virada)

rf_inde = RandomForestRegressor(random_state=42)
rf_inde.fit(X_train, y_train_inde)

# Salvar os modelos
with open('rf_pedra_model.pkl', 'wb') as f:
    pickle.dump(rf_pedra, f)

with open('rf_virada_model.pkl', 'wb') as f:
    pickle.dump(rf_virada, f)

with open('rf_inde_model.pkl', 'wb') as f:
    pickle.dump(rf_inde, f)

# Carregar os modelos treinados
with open('rf_pedra_model.pkl', 'rb') as f:
    rf_pedra = pickle.load(f)

with open('rf_virada_model.pkl', 'rb') as f:
    rf_virada = pickle.load(f)

with open('rf_inde_model.pkl', 'rb') as f:
    rf_inde = pickle.load(f)

# Calcular acurácia dos modelos
pedra_accuracy = accuracy_score(y_test_pedra, rf_pedra.predict(X_test))
virada_accuracy = accuracy_score(y_test_virada, rf_virada.predict(X_test))

# Criar interface no Streamlit
st.title("Previsão de Pedra, Ponto de Virada e INDE para 2023")

# Selecionar o ID_ALUNO
id_aluno = st.selectbox("Escolha o ID do Aluno", df['ID_ALUNO'].unique())

# Filtrar os dados do aluno selecionado
aluno_data = df[df['ID_ALUNO'] == id_aluno].sort_values(by='ano')

# Verificar se os dados do aluno estão disponíveis
if not aluno_data.empty:
    # Preparar os dados do aluno para 2023
    ano_ingresso = aluno_data['ANO_INGRESSO'].values[0]
    inde_2022 = aluno_data[aluno_data['ano'] == 2022]['INDE'].values[0] if 2022 in aluno_data['ano'].values else 7.5
    ano = 2023  # Ano de previsão

    # Dados para previsão
    input_data = np.array([[ano_ingresso, inde_2022, ano]])
    input_data_scaled = scaler.transform(input_data)

    # Fazer previsões
    pred_pedra = rf_pedra.predict(input_data_scaled)
    pred_virada = rf_virada.predict(input_data_scaled)
    pred_inde = rf_inde.predict(input_data_scaled)

    # Traduzir a previsão de pedra para o valor original
    pedra_pred = label_encoder_pedra.inverse_transform(pred_pedra)

    # Mostrar acurácia dos modelos
    st.write(f"Acurácia do modelo para previsão de Pedra: {pedra_accuracy:.2f}")
    st.write(f"Acurácia do modelo para previsão de Ponto de Virada: {virada_accuracy:.2f}")

    # Exibir resultados
    st.write(f"**Previsão de Pedra para 2023**: {pedra_pred[0]}")
    st.write(f"**O aluno estará em ponto de virada em 2023**: {'Sim' if pred_virada[0] == 1 else 'Não'}")

    # Plotar o gráfico de INDE de 2020 a 2023
    inde_history = aluno_data[['ano', 'INDE']].set_index('ano')
    inde_history.loc[2023] = pred_inde[0]  # Adicionar previsão de 2023

    st.write("### Evolução do INDE do aluno (2020-2023)")
    fig, ax = plt.subplots()
    inde_history.plot(ax=ax, marker='o', linestyle='-', color='b')
    ax.set_title(f'Evolução do INDE do Aluno {id_aluno}')
    ax.set_ylabel('INDE')
    ax.set_xlabel('Ano')
    ax.axvline(x=2023, color='r', linestyle='--', label='Previsão para 2023')
    ax.legend()
    st.pyplot(fig)

else:
    st.write("Nenhum dado encontrado para o ID de aluno selecionado.")


