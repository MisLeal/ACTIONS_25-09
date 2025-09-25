import pandas as pd
import streamlit as st
from datetime import date

# ================================
# CONFIGURAÇÕES INICIAIS
# ================================
st.set_page_config(layout='wide')
st.title('ACTIONS TELEVENDAS :chart_with_upwards_trend:')

# ================================
# FUNÇÕES AUXILIARES
# ================================

# Função com cache para carregar os dados
@st.cache_data
def carregar_dados():
    dados = pd.read_csv('dados_analisados.csv')
    hora = pd.read_csv('HORA.csv')
    return dados, hora

# Função para colorir colunas numéricas
def color_total(val):
    if val > 130:
        return 'background-color: green; color: white'
    elif val < 130:
        return 'background-color: yellow; color: black'
    else:
        return ''

# ================================
# CARREGANDO DADOS COM CACHE
# ================================
dados, hora = carregar_dados()

# Ajustes nos dados
dados['SUPERVISOR'] = dados['SUPERVISOR'].str.upper()
hora['SUPERVISOR'] = hora['SUPERVISOR'].str.upper()

# Convertendo datas
dados['fecha_accion'] = pd.to_datetime(dados['fecha_accion'], errors='coerce')
hora['DATA'] = pd.to_datetime(hora['DATA'], errors='coerce')

# Removendo datas inválidas
dados = dados.dropna(subset=['fecha_accion'])
hora = hora.dropna(subset=['DATA'])

# ================================
# PREPARANDO FILTROS
# ================================
hoje = date.today()

datas_dados = dados[dados['fecha_accion'].dt.date <= hoje]['fecha_accion'].dt.date.unique()
datas_hora = hora[hora['DATA'].dt.date <= hoje]['DATA'].dt.date.unique()
datas_disponiveis = sorted(set(datas_dados) | set(datas_hora), reverse=True)

opcoes_datas = ['Todas as datas'] + [str(data) for data in datas_disponiveis]

todos_supervisores = sorted(set(dados['SUPERVISOR'].dropna().unique()) | set(hora['SUPERVISOR'].dropna().unique()))

# ================================
# SIDEBAR - FILTROS
# ================================
st.sidebar.header('Filtros')

# Filtro por data
data_selecionada = st.sidebar.selectbox('📅 Selecione uma data:', opcoes_datas, index=0)

# Filtro por supervisor
supervisores_selecionados = st.sidebar.multiselect(
    '👤 Selecione Supervisor(es):',
    options=todos_supervisores,
    default=[]  # Nenhum selecionado por padrão
)

# ================================
# APLICANDO FILTROS (independentes)
# ================================
dados_filtrados = dados.copy()
hora_filtrada = hora.copy()

# Filtro por data
if data_selecionada != 'Todas as datas':
    data_filtro = pd.to_datetime(data_selecionada).date()
    dados_filtrados = dados_filtrados[dados_filtrados['fecha_accion'].dt.date == data_filtro]
    hora_filtrada = hora_filtrada[hora_filtrada['DATA'].dt.date == data_filtro]

# Filtro por supervisor
if supervisores_selecionados:
    dados_filtrados = dados_filtrados[dados_filtrados['SUPERVISOR'].isin(supervisores_selecionados)]
    hora_filtrada = hora_filtrada[hora_filtrada['SUPERVISOR'].isin(supervisores_selecionados)]

# ================================
# EXIBIÇÃO PRINCIPAL
# ================================
coluna1, coluna2 = st.columns(2)

with coluna1:
    st.header("ACTIONS :pushpin:")
    if not dados_filtrados.empty:
        st.dataframe(
            dados_filtrados.style.applymap(color_total, subset=['Total']),
            use_container_width=True
        )
    else:
        st.warning("Nenhum dado encontrado para os filtros selecionados.")

with coluna2:
    st.header('CRM 💼')
    if not hora_filtrada.empty:
        st.dataframe(
            hora_filtrada[['NOME', 'GESTIONES', 'DATA', 'SUPERVISOR', 'CONTATO DIRETO']].style.applymap(color_total, subset=['GESTIONES']),
            use_container_width=True
        )
    else:
        st.warning("Nenhum dado encontrado para os filtros selecionados.")
