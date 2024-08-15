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
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score, mean_squared_error
import plotly.express as px
import plotly.graph_objects as go
from statsmodels.tsa.arima.model import ARIMA

# Cacheamento para melhorar o desempenho
@st.cache_data
def carregar_dados(file_path):
    df = pd.read_csv(file_path)
    alunos_completos = df.groupby('ID_ALUNO').filter(lambda x: x['ano'].max() == 2022)
    return alunos_completos

@st.cache_resource
def treinar_modelos(X_train, y_train_pedra, y_train_virada):
    param_grid = {
        'n_estimators': [100],
        'max_depth': [None],
        'min_samples_split': [2],
        'min_samples_leaf': [1]
    }
    grid_search_pedra = GridSearchCV(RandomForestClassifier(random_state=42), param_grid, cv=5)
    grid_search_pedra.fit(X_train, y_train_pedra)
    rf_pedra = grid_search_pedra.best_estimator_

    grid_search_virada = GridSearchCV(RandomForestClassifier(random_state=42), param_grid, cv=5)
    grid_search_virada.fit(X_train, y_train_virada)
    rf_virada = grid_search_virada.best_estimator_

    return rf_pedra, rf_virada

@st.cache_data
def preparar_dados(alunos_completos):
    label_encoder_pedra = LabelEncoder()
    label_encoder_virada = LabelEncoder()

    alunos_completos['PEDRA'] = label_encoder_pedra.fit_transform(alunos_completos['PEDRA'])
    alunos_completos['PONTO_VIRADA'] = label_encoder_virada.fit_transform(alunos_completos['PONTO_VIRADA'])

    X = alunos_completos[['ANO_INGRESSO', 'INDE', 'ano']]
    y_pedra = alunos_completos['PEDRA']
    y_virada = alunos_completos['PONTO_VIRADA']

    X_train, X_test, y_train_pedra, y_test_pedra = train_test_split(X, y_pedra, test_size=0.2, random_state=42)
    _, _, y_train_virada, y_test_virada = train_test_split(X, y_virada, test_size=0.2, random_state=42)

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    return X_train, X_test, y_train_pedra, y_test_pedra, y_train_virada, y_test_virada, scaler, label_encoder_pedra, label_encoder_virada

# Carregar dados e preparar
file_path = 'BD_modelo.csv'
alunos_completos = carregar_dados(file_path)
X_train, X_test, y_train_pedra, y_test_pedra, y_train_virada, y_test_virada, scaler, label_encoder_pedra, label_encoder_virada = preparar_dados(alunos_completos)

# Treinar modelos com caching
rf_pedra, rf_virada = treinar_modelos(X_train, y_train_pedra, y_train_virada)

# Fazer previsões e inverter a transformação para garantir que os tipos e valores estejam corretos
pedra_predicoes = rf_pedra.predict(X_test)
virada_predicoes = rf_virada.predict(X_test)

# Verifique as dimensões e tipos de dados antes de calcular a acurácia
try:
    if len(y_test_pedra) != len(pedra_predicoes):
        raise ValueError("Dimensões não correspondem entre y_test_pedra e pedra_predicoes")

    # Calcular acurácia dos modelos de PEDRA e PONTO_VIRADA
    pedra_accuracy = accuracy_score(y_test_pedra, pedra_predicoes)
    virada_accuracy = accuracy_score(y_test_virada, virada_predicoes)

except ValueError as e:
    st.error(f"Erro ao calcular a acurácia: {e}")
    st.stop()

# Customização do tema da aplicação
st.set_page_config(page_title="Previsão Acadêmica", layout="wide", initial_sidebar_state="expanded")

# Função para exibir a seção de ajuda
def exibir_ajuda():
    st.sidebar.title("Ajuda")
    st.sidebar.info("""
    **Previsão de Pedra, Ponto de Virada e INDE:**
    - **PEDRA**: Indicador de desempenho acadêmico que mede a resiliência do aluno em continuar no curso.
    - **PONTO_VIRADA**: Identifica o ponto em que um aluno pode mudar seu desempenho significativamente.
    - **INDE**: Índice que mede o desempenho acadêmico geral do aluno.
    
    **Navegação:**
    Use a barra lateral para explorar diferentes funcionalidades da aplicação.
    """)

# Exibir a seção de ajuda na barra lateral
exibir_ajuda()

# Barra lateral de navegação
st.sidebar.title("Navegação")
opcao = st.sidebar.radio("Ir para", ["Visão Geral", "Análise Comparativa", "Simulação 'What-If'", "Métricas dos Modelos"])

# Visão Geral
if opcao == "Visão Geral":
    st.title("Visão Geral da Aplicação")
    st.write("""
    Esta aplicação permite a previsão de indicadores acadêmicos como PEDRA, PONTO_VIRADA e INDE.
    Utilize a barra lateral para navegar entre as diferentes funcionalidades.
    """)

# Análise Comparativa de Múltiplos Alunos
elif opcao == "Análise Comparativa":
    st.title("Análise Comparativa de Múltiplos Alunos")
    comparar_ids = st.multiselect("Selecione IDs de alunos para comparação", alunos_completos['ID_ALUNO'].unique())

    if comparar_ids:
        alunos_data = alunos_completos[alunos_completos['ID_ALUNO'].isin(comparar_ids)].sort_values(by='ano')
        
        st.write("## Tendência do INDE ao longo do tempo")
        fig = px.line(alunos_data, x='ano', y='INDE', color='ID_ALUNO', markers=True)
        fig.update_layout(height=500)  # Aumentar o tamanho do gráfico
        st.plotly_chart(fig, use_container_width=True)
        
        st.write("## Correlação entre INDE, PEDRA, e PONTO_VIRADA")
        correlation = alunos_completos[['INDE', 'PEDRA', 'PONTO_VIRADA']].corr()
        fig_corr = go.Figure(data=go.Heatmap(
            z=correlation.values,
            x=correlation.columns,
            y=correlation.columns,
            colorscale='Blues'  # Ajuste de cor para combinar com os gráficos de linhas
        ))
        st.plotly_chart(fig_corr, use_container_width=True)

# Simulação de Cenários "What-If"
elif opcao == "Simulação 'What-If'":
    st.title("Simulação de Cenários 'What-If'")
    sim_id = st.selectbox("Selecione o ID do Aluno para Simulação", alunos_completos['ID_ALUNO'].unique())
    sim_inde = st.number_input("Projeção de INDE para 2023 (Simulação)", value=50.0, min_value=0.0, max_value=100.0)

    input_simulation = np.array([[alunos_completos.loc[alunos_completos['ID_ALUNO'] == sim_id, 'ANO_INGRESSO'].values[0], sim_inde, 2023]])
    input_simulation_scaled = scaler.transform(input_simulation)

    sim_pred_pedra = rf_pedra.predict(input_simulation_scaled)
    sim_pred_virada = rf_virada.predict(input_simulation_scaled)

    sim_pedra_pred = label_encoder_pedra.inverse_transform(sim_pred_pedra)

    st.write(f"**Previsão Simulada de Pedra para 2023:** **{sim_pedra_pred[0]}**")
    st.write(f"**Ponto de Virada em 2023 (Simulado):** **{'Sim' if sim_pred_virada[0] == 1 else 'Não'}**")

# Métricas dos Modelos
elif opcao == "Métricas dos Modelos":
    st.title("Métricas dos Modelos")

    st.write(f"**Acurácia para previsão de Pedra:** **{pedra_accuracy:.2f}**")
    st.write(f"**Acurácia para previsão de Ponto de Virada:** **{virada_accuracy:.2f}**")

    # Análise Preditiva Avançada: Adicionando explicações
    if st.button("Gerar Explicações com SHAP"):
        import shap
        st.write("### Importância das Variáveis")
        explainer_pedra = shap.TreeExplainer(rf_pedra)
        shap_values_pedra = explainer_pedra.shap_values(X_test)
        shap.summary_plot(shap_values_pedra, X_test, feature_names=['ANO_INGRESSO', 'INDE', 'ano'], plot_type="bar")
        st.pyplot(bbox_inches='tight')

        explainer_virada = shap.TreeExplainer(rf_virada)
        shap_values_virada = explainer_virada.shap_values(X_test)
        shap.summary_plot(shap_values_virada, X_test, feature_names=['ANO_INGRESSO', 'INDE', 'ano'], plot_type="bar")
        st.pyplot(bbox_inches='tight')

    if 'arima_rmse' in locals() and arima_rmse is not None:
        st.write(f"**RMSE para previsão de INDE:** **{arima_rmse:.2f}**")

# Mostrar dados brutos (opcional)
if st.sidebar.checkbox("Mostrar dados brutos dos alunos"):
    st.write(alunos_completos)
