import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt


st.set_page_config(layout="centered")

# Dados diurnos
data_diurno = {
    "SÉRIE": ["APROVADOS", "APROVADOS COM RPP", "REPROVADOS", "DESISTENTES", "TOTAL DE ALUNOS MATRICULADOS"],
    "1º Ano": [157, 83, 1, 11, 241],
    "2º Ano": [92, 86, 3, 14, 181],
    "RFM SEG. IV (1ª SÉRIE - 2ª SÉRIE)": [55, 0, 0, 8, 63],
    "RFM SEG. V (2ª SÉRIE - 3ª SÉRIE)": [21, 0, 3, 14, 24],
    "3ª SÉRIE": [160, 0, 0, 6, 160]
}

# Dados noturnos
data_noturno = {
    "SÉRIE": ["APROVADOS", "APROVADOS COM RPP", "REPROVADOS", "DESISTENTES", "TOTAL DE ALUNOS MATRICULADOS"],
    "TJ6": [58, 0, 12, 33, 70],
    "TF6": [65, 0, 4, 132, 69],
    "TF7": [158, 0, 7, 52, 165]
}

df_diurno = pd.DataFrame(data_diurno)
df_noturno = pd.DataFrame(data_noturno)

# Configuração do Streamlit
st.title("📊 Desempenho CETI 2024")
st.markdown("---")

# Seleção do turno
turno = st.segmented_control("Selecione o Turno:", ["Diurno", "Noturno"])
st.markdown("---")

if turno == "Diurno":
    df = df_diurno
    series_options = ["1º Ano", "2º Ano", "RFM SEG. IV (1ª SÉRIE - 2ª SÉRIE)", 
                     "RFM SEG. V (2ª SÉRIE - 3ª SÉRIE)", "3ª SÉRIE"]
else:
    df = df_noturno
    series_options = ["TJ6", "TF6", "TF7"]
st.dataframe(df)
# Seleção da série
selected_series = st.segmented_control("Selecione a Série:", series_options)
if not selected_series:
    st.stop()
# Extrair dados
aprovados = df[selected_series].iloc[0]
aprovados_rpp = df[selected_series].iloc[1]
reprovados = df[selected_series].iloc[2]
desistentes = df[selected_series].iloc[3]
matriculados = df[selected_series].iloc[4]

# --- Gráfico 1: Barras Horizontais ---
fig1, ax1 = plt.subplots(figsize=(12, 4))
categories = ["Aprovados (Total)", "Reprovados", "Matriculados"]
values = [aprovados + aprovados_rpp, reprovados, matriculados]
colors = ['#2e7d32', '#d32f2f', '#1976d2']

# Barra de Aprovados (empilhada)
ax1.barh(categories[0], aprovados, color='#2e7d32', label='Aprovados')
ax1.barh(categories[0], aprovados_rpp, left=aprovados, color='#81c784', label='Aprovados com RPP')

# Demais barras
ax1.barh(categories[1], reprovados, color='#d32f2f')
ax1.barh(categories[2], matriculados, color='#1976d2')

# Adicionar valores
for i, (category, value) in enumerate(zip(categories, values)):
    if i == 0:  # Caso especial para barra empilhada
        ax1.text(aprovados/2, i, f"Aprovados: {aprovados}", ha='center', va='center', color='white')
        ax1.text(aprovados + aprovados_rpp/2, i, f"RPP: {aprovados_rpp}", ha='center', va='center', color='white')
    else:
        ax1.text(value/2, i, f"{value}", ha='center', va='center', color='white')

ax1.set_title(f"Distribuição Principal - {selected_series} ({turno})", fontsize=14)
ax1.set_xlim(0, max(values)*1.1)
ax1.legend(loc='lower right', bbox_to_anchor=(1, -0.3), ncol=2)

# --- Gráfico 2: Pizza (Aprovados/RPP/Reprovados) ---
fig2, ax2 = plt.subplots(figsize=(6, 6))
labels_pie1 = ['Aprovados', 'Aprovados com RPP', 'Reprovados']
sizes_pie1 = [aprovados, aprovados_rpp, reprovados]
colors_pie1 = ['#2e7d32', '#81c784', '#d32f2f']

def autopct_format(values):
    def my_autopct(pct):
        total = sum(values)
        val = int(round(pct*total/100.0))
        return f'{val}\n({pct:.1f}%)'
    return my_autopct

wedges, texts, autotexts = ax2.pie(
    sizes_pie1, 
    labels=labels_pie1, 
    autopct=autopct_format(sizes_pie1),
    colors=colors_pie1,
    startangle=90,
    textprops={'fontsize': 10}
)

# Anotação do total fora do gráfico
ax2.text(-1.4, 0.5, f"Total Matriculados:\n{matriculados}", 
         ha='center', va='center', fontsize=12, 
         bbox=dict(facecolor='white', edgecolor='gray'))

ax2.set_title("Distribuição de Resultados Finais", fontsize=12)

# --- Gráfico 3: Pizza (Matriculados vs Desistentes) ---
fig3, ax3 = plt.subplots(figsize=(6, 6))
labels_pie2 = ['Matriculados', 'Desistentes']
sizes_pie2 = [matriculados, desistentes]
colors_pie2 = ['#1976d2', '#607d8b']

ax3.pie(
    sizes_pie2, 
    labels=labels_pie2, 
    autopct=autopct_format(sizes_pie2),
    colors=colors_pie2,
    startangle=90,
    textprops={'fontsize': 10}
)
ax3.set_title("Proporção de Retenção vs Desistência", fontsize=12)

# --- Renderização no Streamlit ---
st.markdown("---")
st.pyplot(fig1)
st.markdown("---")
st.pyplot(fig2)
st.markdown("---")
st.pyplot(fig3)
