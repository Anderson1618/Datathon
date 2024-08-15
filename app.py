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

# Explicação sobre a ONG Passos Mágicos
st.title("ONG Passos Mágicos")
st.write("""
A **ONG Passos Mágicos** é uma organização dedicada a apoiar crianças e adolescentes em situação de vulnerabilidade, proporcionando-lhes oportunidades de desenvolvimento pessoal, educacional e profissional. Através de diversas atividades e programas, a ONG visa transformar vidas e construir um futuro mais promissor para os jovens que atende.

Este projeto, em colaboração com a ONG, visa monitorar e prever indicadores acadêmicos cruciais, como o Índice de Desenvolvimento Educacional (INDE), a resiliência representada pela Pedra, e os pontos de virada, onde mudanças significativas no desempenho podem ocorrer. Essas previsões ajudam a identificar e intervir de forma mais eficaz na trajetória educacional dos alunos, garantindo que recebam o apoio necessário no momento certo.
""")

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
st.title("Projeção de Pedra, Ponto de Virada e INDE para 2023")

# Análise Comparativa de Múltiplos Alunos
st.write("## Análise Comparativa de Múltiplos Alunos")
comparar_ids = st.multiselect("Selecione IDs de alunos para comparação", alunos_completos['ID_ALUNO'].unique())

# Filtrar os dados dos alunos selecionados
alunos_data = alunos_completos[alunos_completos['ID_ALUNO'].isin(comparar_ids)].sort_values(by='ano')

# Gráficos de Tendências
if not alunos_data.empty:
    st.write("## Tendência do INDE ao longo do tempo para Alunos Selecionados")
    fig = px.line(alunos_data, x='ano', y='INDE', color='ID_ALUNO', markers=True)
    st.plotly_chart(fig)

    st.write("---")

    # Correlação entre INDE, PEDRA, e PONTO_VIRADA
    st.write("## Correlação entre INDE, PEDRA, e PONTO_VIRADA")
    st.write("""
    ### O que é a Correlação?

    A correlação é uma medida estatística que indica a força e a direção do relacionamento entre duas ou mais variáveis. Na educação, compreender a correlação entre diferentes indicadores de desempenho dos alunos pode fornecer insights valiosos sobre como esses indicadores se influenciam mutuamente.

    ### Interpretação das Correlações

    Nesta seção, exploramos a correlação entre três indicadores críticos:

    1. **INDE (Índice de Desenvolvimento Educacional)**: Mede o desempenho acadêmico geral do aluno.
    2. **PEDRA**: Representa a resiliência do aluno, ou seja, a sua capacidade de superar desafios e persistir nos estudos.
    3. **PONTO_VIRADA**: Indica um ponto crítico onde pode ocorrer uma mudança significativa no desempenho do aluno, seja positiva ou negativa.

    ### Como Ler o Mapa de Calor

    O mapa de calor (heatmap) apresentado a seguir mostra as correlações entre INDE, PEDRA e PONTO_VIRADA:

    - **Correlação Positiva**: Um valor positivo indica que, à medida que um indicador aumenta, o outro também tende a aumentar. Por exemplo, se houver uma correlação positiva alta entre INDE e PEDRA, isso sugere que alunos com alto desempenho acadêmico (INDE) também tendem a mostrar alta resiliência (PEDRA).
    - **Correlação Negativa**: Um valor negativo indica que, à medida que um indicador aumenta, o outro tende a diminuir. Por exemplo, se houver uma correlação negativa entre PEDRA e PONTO_VIRADA, isso pode sugerir que alunos mais resilientes têm menos probabilidade de experimentar uma mudança abrupta em seu desempenho.
    - **Correlação Próxima de Zero**: Indica pouca ou nenhuma relação linear entre os indicadores. Isso significa que as mudanças em um indicador não têm um efeito previsível sobre o outro.

    ### Utilidade da Correlação

    Entender as correlações entre esses indicadores pode ajudar a ONG Passos Mágicos a identificar padrões e tomar decisões mais informadas. Por exemplo, se a ONG perceber que a resiliência (PEDRA) está fortemente correlacionada com o desempenho acadêmico (INDE), pode concentrar seus esforços em fortalecer a resiliência dos alunos para melhorar seu desempenho geral.

    A análise das correlações também pode ajudar a identificar quais alunos estão em risco de enfrentar um ponto de virada negativo e precisar de intervenção imediata.
    """)

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

    # Título e explicação para os gráficos de projeção de INDE
    st.write("## Projeção do INDE para 2023")
    st.write("""
    **Projeção do INDE para 2023:**
    Os gráficos a seguir mostram a evolução do Índice de Desenvolvimento Educacional (INDE) ao longo dos últimos anos para os alunos selecionados, 
    incluindo a projeção para 2023 com base nos dados anteriores. O INDE é um indicador chave do desempenho acadêmico do aluno, e a projeção para 2023 
    fornece uma visão sobre a tendência futura, permitindo intervenções estratégicas para apoiar o sucesso acadêmico contínuo.
    """)

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

            # Calcular erro (RMSE) do modelo ARIMA
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

                # Adicionar título ao gráfico
                fig.update_layout(title=f'Projeção do INDE para 2023 - Aluno {id_aluno}',
                                  xaxis_title='Ano',
                                  yaxis_title='INDE',
                                  height=400)  # Aumentar o tamanho do gráfico

                # Exibir gráfico
                st.plotly_chart(fig)

    st.write("---")

# Simulação de Cenários 'What-If'
st.write("## Simulação de Cenários 'What-If'")
st.write("""
### O que é a Simulação de Cenários?

A Simulação de Cenários 'What-If' permite explorar como diferentes condições podem impactar os resultados acadêmicos dos alunos. Ao ajustar a projeção do Índice de Desenvolvimento Educacional (INDE) para um ano específico, podemos prever como essa alteração pode afetar outros indicadores, como a resiliência (representada pela Pedra) e a ocorrência de um ponto de virada no desempenho do aluno.

#### Como utilizar a Simulação?

1. **Selecione o ID do Aluno**: Escolha um aluno específico da lista de IDs disponíveis.
2. **Projeção de INDE para 2023**: Ajuste o valor do INDE para 2023, que representa sua projeção sobre o desempenho do aluno para o próximo ano. Esse valor pode variar entre 0 e 10.
3. **Interprete os Resultados**: Com base nos dados inseridos, a aplicação irá prever:
   - **Pedra**: A probabilidade de que o aluno mantenha sua resiliência acadêmica.
   - **Ponto de Virada**: A probabilidade de que o aluno experimente uma mudança significativa em seu desempenho.

Essa funcionalidade é crucial para ajudar a ONG Passos Mágicos a tomar decisões informadas sobre onde e como intervir no desenvolvimento educacional de cada aluno, garantindo que cada um deles receba o apoio necessário para alcançar seu pleno potencial.
""")

sim_id = st.selectbox("Selecione o ID do Aluno para Simulação", alunos_completos['ID_ALUNO'].unique())
sim_inde = st.number_input("Projeção de INDE para 2023 (Simulação)", value=5.0, min_value=0.0, max_value=10.0)

# Preparar dados de entrada simulados
input_simulation = np.array([[alunos_completos.loc[alunos_completos['ID_ALUNO'] == sim_id, 'ANO_INGRESSO'].values[0], sim_inde, 2023]])
input_simulation_scaled = scaler.transform(input_simulation)

# Fazer projeções com os dados simulados
sim_pred_pedra = rf_pedra.predict(input_simulation_scaled)
sim_pred_virada = rf_virada.predict(input_simulation_scaled)

# Traduzir a projeção de pedra para o valor original
sim_pedra_pred = label_encoder_pedra.inverse_transform(sim_pred_pedra)

# Exibir resultados da simulação
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

# Opcional: Mostrar os dados brutos (para análise detalhada)
if st.checkbox("Mostrar dados brutos dos alunos"):
    st.write(alunos_completos)
