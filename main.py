import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(layout="wide")

# Backup/Restore discreto
with st.expander("⚙️ Dados", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        uploaded = st.file_uploader("Restaurar backup", type="pkl", label_visibility="collapsed", key="pkl_upload")
        if uploaded and st.session_state.get("last_upload") != uploaded.name:
            st.session_state.last_upload = uploaded.name
            st.session_state.data = pd.read_pickle(uploaded)
            with open("data_pickle.pkl", "wb") as f:
                f.write(uploaded.getvalue())
            st.success("Restaurado!")
            st.rerun()
    with col2:
        try:
            with open("data_pickle.pkl", "rb") as f:
                st.download_button("⬇ Baixar backup", f.read(), "data_pickle.pkl", use_container_width=True)
        except FileNotFoundError:
            st.caption("Nenhum dado salvo ainda")

# Dados
data_diurno = {
    "SÉRIE": ["APROVADOS", "APROVADOS COM RPP", "REPROVADOS", "DESISTENTES", "TOTAL DE ALUNOS MATRICULADOS"],
    "1º Ano": [157, 83, 1, 11, 241], "2º Ano": [92, 86, 3, 14, 181],
    "RFM SEG. IV (1ª SÉRIE - 2ª SÉRIE)": [55, 0, 0, 8, 63],
    "RFM SEG. V (2ª SÉRIE - 3ª SÉRIE)": [21, 0, 3, 14, 24], "3ª SÉRIE": [160, 0, 0, 6, 160]
}
data_noturno = {
    "SÉRIE": ["APROVADOS", "APROVADOS COM RPP", "REPROVADOS", "DESISTENTES", "TOTAL DE ALUNOS MATRICULADOS"],
    "TJ6": [58, 0, 12, 33, 70], "TF6": [65, 0, 4, 132, 69], "TF7": [158, 0, 7, 52, 165], "TJ7": [120, 0, 10, 30, 140]
}
data_area = {
    "Área do Conhecimento": ["APROVADOS", "APROVADOS COM RPP", "REPROVADOS", "DESISTENTES", "TOTAL DE ALUNOS MATRICULADOS"],
    "Linguagens": [0]*5, "Matemática": [0]*5, "Ciências da Natureza": [0]*5, "Ciências Humanas": [0]*5
}

# Carregar/salvar dados
if "data" not in st.session_state:
    try:
        st.session_state.data = pd.read_pickle("data_pickle.pkl")
    except FileNotFoundError:
        st.session_state.data = {"diurno": pd.DataFrame(data_diurno), "noturno": pd.DataFrame(data_noturno), "area_do_conhecimento": pd.DataFrame(data_area)}

turnos = {"Diurno": "diurno", "Noturno": "noturno", "Área do Conhecimento": "area_do_conhecimento"}
idx_cols = {"diurno": "SÉRIE", "noturno": "SÉRIE", "area_do_conhecimento": "Área do Conhecimento"}

st.title("📊 Desempenho CETI 2025")
turno = st.segmented_control("Recorte:", list(turnos.keys()))
if not turno: st.stop()

chave = turnos[turno]
df = st.session_state.data[chave].set_index(idx_cols[chave])
df_edited = st.data_editor(df, key=f"editor_{chave}")

if not df_edited.equals(df):
    st.session_state.data[chave] = df_edited.reset_index()
    pd.to_pickle(st.session_state.data, "data_pickle.pkl")
    st.rerun()

serie = st.segmented_control("Série:", df.columns.tolist())
if not serie or df[serie].sum() == 0:
    st.warning("Selecione uma série com dados.") if serie else None
    st.stop()

aprov, rpp, reprov, desist, matric = df[serie].tolist()
cores = ["#2e7d32", "#81c784", "#d32f2f", "#607d8b", "#1976d2"]

# Gráficos em tabs (fontes grandes para projeção)
tab1, tab2, tab3 = st.tabs(["Gráfico 1", "Gráfico 2", "Gráfico 3"])

with tab1:
    fig1 = px.bar(x=[aprov, rpp, reprov, matric], y=["Aprovados", "com RPP", "Reprovados", "Matriculados"], 
                  orientation="h", color_discrete_sequence=cores, text_auto=True)
    fig1.update_layout(showlegend=False, height=350, margin=dict(l=0,r=0,t=60,b=0), 
                       title=dict(text=f"Distribuição - {serie}", font=dict(size=28)),
                       yaxis=dict(tickfont=dict(size=22), title=None),
                       xaxis=dict(visible=False))
    fig1.update_traces(textfont_size=24)
    st.plotly_chart(fig1, use_container_width=True)

with tab2:
    fig2 = px.pie(values=[aprov, rpp, reprov], names=["Aprovados", "com RPP", "Reprovados"], 
                  color_discrete_sequence=cores[:3], hole=0.3)
    fig2.update_layout(height=500, margin=dict(l=0,r=0,t=60,b=0), 
                       title=dict(text="Resultados Finais", font=dict(size=28)),
                       legend=dict(font=dict(size=20)))
    fig2.update_traces(textinfo="value+percent", textposition="inside", textfont_size=22)
    st.plotly_chart(fig2, use_container_width=True)

with tab3:
    fig3 = px.pie(values=[matric, desist], names=["Matriculados", "Desistentes"], 
                  color_discrete_sequence=[cores[4], cores[3]], hole=0.3)
    fig3.update_layout(height=500, margin=dict(l=0,r=0,t=60,b=0), 
                       title=dict(text="Permanência", font=dict(size=28)),
                       legend=dict(font=dict(size=20)))
    fig3.update_traces(textinfo="value+percent", textposition="inside", textfont_size=22)
    st.plotly_chart(fig3, use_container_width=True)
