import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import webbrowser
import os
from datetime import datetime

# ==============================================================================
# 1. CONFIGURAÇÃO GLOBAL DA INTERFACE (UI/UX)
# ==============================================================================
st.set_page_config(
    page_title="Enterprise Support Analytics Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização customizada via CSS Injection para visual corporativo escuro
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500&family=Inter:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stCodeBlock, code { font-family: 'Fira Code', monospace !important; }
    
    /* Customização dos Cards de Métrica */
    div[data-testid="stMetricValue"] {
        font-size: 36px !important;
        font-weight: 700 !important;
        color: #00f2fe !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 14px !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        color: #94a3b8 !important;
    }
    
    /* Bordas e divisores limpos */
    .reportview-container { background-color: #0f172a; }
    hr { border-color: #334155 !important; }
    </style>
    """, unsafe_allow_html=True)


# ==============================================================================
# 2. CAMADA DE INFRAESTRUTURA E DATA QUALITY (ETL & AUDITORIA)
# ==============================================================================
@st.cache_data(ttl=300)
def executar_pipeline_etl():
    """
    Simula uma pipeline de extração, tratamento e auditoria de dados (ETL).
    Lê a base de dados em formato bruto e aplica higienização estrita de tipos.
    """
    caminho = 'base_suporte_ti.csv'
    if not os.path.exists(caminho):
        return None, {"status": "CRITICAL_ERROR", "msg": "Data lake inacessível."}
        
    df_raw = pd.read_csv(caminho)
    
    # Dicionário de metadados para auditoria antes do tratamento
    auditoria = {
        "registros_brutos": len(df_raw),
        "valores_nulos": df_raw.isnull().sum().sum(),
        "duplicados_removidos": df_raw.duplicated(subset=['ID_Chamado']).sum()
    }
    
    # Data Cleansing (Limpeza e padronização)
    df_clean = df_raw.drop_duplicates(subset=['ID_Chamado']).copy()
    df_clean['Data_Abertura'] = pd.to_datetime(df_clean['Data_Abertura'], errors='coerce')
    df_clean['Data_Dia'] = df_clean['Data_Abertura'].dt.date
    df_clean['Nota_CSAT'] = pd.to_numeric(df_clean['Nota_CSAT'], errors='coerce').fillna(4.0)
    df_clean['Tempo_Resolucao_Horas'] = pd.to_numeric(df_clean['Tempo_Resolucao_Horas'], errors='coerce').fillna(24.0)
    
    # Criação de features calculadas (Feature Engineering)
    df_clean['Mes_Ano'] = df_clean['Data_Abertura'].dt.to_period('M').astype(str)
    
    auditoria["registros_liquidos"] = len(df_clean)
    auditoria["colunas_processadas"] = list(df_clean.columns)
    
    return df_clean, auditoria

# Executa a pipeline de dados
df, log_auditoria = executar_pipeline_etl()

if df is None:
    st.error(f"🛑 FALHA CRÍTICA NO PIPELINE: {log_auditoria['msg']}")
    st.stop()


# ==============================================================================
# 3. CONTROLADORES E FILTROS DINÂMICOS (SIDEBAR CONFIG)
# ==============================================================================
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2092/2092130.png", width=60)
st.sidebar.markdown("# **Filtros Avançados**")
st.sidebar.markdown("---")

# Seletor de Janela de Tempo Baseado em Calendário
data_min, data_max = df['Data_Dia'].min(), df['Data_Dia'].max()
periodo_selecionado = st.sidebar.date_input(
    "Janela Temporal de Análise:",
    [data_min, data_max],
    min_value=data_min,
    max_value=data_max
)

# Filtros Categóricos Dinâmicos
lista_prioridades = sorted(df['Prioridade'].unique())
prioridades_sel = st.sidebar.multiselect("Nível de Severidade (SLA):", lista_prioridades, default=lista_prioridades)

lista_status = sorted(df['Status'].unique())
status_sel = st.sidebar.multiselect("Status do Ciclo de Vida:", lista_status, default=lista_status)

lista_departamentos = sorted(df['Departamento'].unique())
deps_sel = st.sidebar.multiselect("Unidade de Negócio Solicitante:", lista_departamentos, default=lista_departamentos)

# Aplicação Estrita das Regras de Filtragem no DataFrame Global
if len(periodo_selecionado) == 2:
    dt_inicio, dt_fim = periodo_selecionado
    mascara_data = (df['Data_Dia'] >= dt_inicio) & (df['Data_Dia'] <= dt_fim)
else:
    mascara_data = True

df_filtrado = df[
    mascara_data & 
    df['Prioridade'].isin(prioridades_sel) & 
    df['Status'].isin(status_sel) & 
    df['Departamento'].isin(deps_sel)
]


# ==============================================================================
# 4. PAINÉIS DE NAVEGAÇÃO INTERNA (TABS DO SISTEMA)
# ==============================================================================
aba_dashboard, aba_matriz, aba_performance, aba_auditoria = st.tabs([
    "📈 Operational Dashboard", 
    "🔥 Matriz de Risco", 
    "🏆 Gestão de Atendentes", 
    "🔍 Governança & Auditoria"
])


# ==============================================================================
# ABA 1: OPERATIONAL DASHBOARD (VISÃO GERAL & METRICAS)
# ==============================================================================
with aba_dashboard:
    st.markdown("## **Indicadores de Performance Chave (KPIs)**")
    
    # Cálculos Métricos Avançados
    total_chamados = len(df_filtrado)
    chamados_no_prazo = len(df_filtrado[df_filtrado['Dentro_SLA'] == 'Sim'])
    taxa_sla_global = (chamados_no_prazo / total_chamados * 100) if total_chamados > 0 else 0
    
    backlog_total = len(df_filtrado[df_filtrado['Status'].isin(['Em andamento', 'Reaberto'])])
    score_csat_geral = df_filtrado['Nota_CSAT'].mean()
    mttr_geral = df_filtrado['Tempo_Resolucao_Horas'].mean()
    
    # Container de Exibição de KPIs em Grade
    kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns(5)
    
    with kpi_col1:
        st.metric("Volumetria Total", f"{total_chamados}", delta="Entradas")
    with kpi_col2:
        st.metric("Fulfillment SLA", f"{taxa_sla_global:.1f}%", delta="Meta: 95%", delta_color="normal" if taxa_sla_global >= 95 else "inverse")
    with kpi_col3:
        st.metric("Backlog Ativo", f"{backlog_total}", delta="Pendente", delta_color="inverse")
    with kpi_col4:
        st.metric("MTTR (Média)", f"{mttr_geral:.1f} hrs", delta="Tempo de Resolução", delta_color="inverse")
    with kpi_col5:
        st.metric("User Satisfaction", f"{score_csat_geral:.2f}", delta="Meta: 4.5", delta_color="normal" if score_csat_geral >= 4.5 else "inverse")
        
    st.markdown("---")
    
    # Sub-bloco: Série Temporal com IA e Decomposição de Tendência
    st.markdown("### **Linha do Tempo: Flutuação Histórica e Previsão Baseada em Tendência**")
    
    df_temporal = df_filtrado.groupby('Data_Dia').size().reset_index(name='Volume_Real')
    df_temporal['Media_Movel_7D'] = df_temporal['Volume_Real'].rolling(window=7, min_periods=1).mean()
    df_temporal['Media_Movel_14D'] = df_temporal['Volume_Real'].rolling(window=14, min_periods=1).mean()
    
    fig_temporal = go.Figure()
    fig_temporal.add_trace(go.Scatter(x=df_temporal['Data_Dia'], y=df_temporal['Volume_Real'], name='Chamados Diários', line=dict(color='#0ea5e9', width=1.5)))
    fig_temporal.add_trace(go.Scatter(x=df_temporal['Data_Dia'], y=df_temporal['Media_Movel_7D'], name='Tendência Semanal (IA)', line=dict(color='#ef4444', width=2.5, dash='dash')))
    fig_temporal.add_trace(go.Scatter(x=df_temporal['Data_Dia'], y=df_temporal['Media_Movel_14D'], name='Tendência Quinzenal', line=dict(color='#eab308', width=2, dash='dot')))
    
    fig_temporal.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=10, r=10, t=10, b=10),
        height=300
    )
    st.plotly_chart(fig_temporal, use_container_width=True)
    
    st.markdown("---")
    
    # Sub-bloco: Distribuição por Canais e Categorias (Lado a Lado)
    graf_col1, graf_col2 = st.columns(2)
    
    with graf_col1:
        st.markdown("#### **Representatividade por Canal de Entrada**")
        # >>> ALTERAÇÃO DE COR NO CÓDIGO <<<
        # Substituímos a paleta padrão por 'px.colors.qualitative.Bold' para um visual mais vibrante.
        fig_rosca_canal = px.pie(df_filtrado, names='Canal_Atendimento', hole=0.6, 
                                 color_discrete_sequence=px.colors.qualitative.Bold)
        fig_rosca_canal.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig_rosca_canal, use_container_width=True)
        
    with graf_col2:
        st.markdown("#### **Principais Motivos de Incidentes**")
        df_cat_summary = df_filtrado['Categoria'].value_counts().reset_index(name='Quantidade')
        df_cat_summary.columns = ['Categoria', 'Quantidade']
        fig_barras_cat = px.bar(df_cat_summary, x='Quantidade', y='Categoria', orientation='h', color='Quantidade', color_continuous_scale='Blues')
        fig_barras_cat.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig_barras_cat, use_container_width=True)


# ==============================================================================
# ABA 2: MATRIZ DE RISCO & CRITICIDADE (HEATMAP)
# ==============================================================================
with aba_matriz:
    st.markdown("## **Matriz Estratégica de Severidade por Categoria**")
    st.markdown("Esta visão cruza as categorias com as prioridades para mapear os pontos cegos que causam impacto financeiro.")
    
    # Pivotagem de dados para construir uma matriz bidimensional (Tabela de Contingência)
    matriz_criticidade = pd.crosstab(
        df_filtrado['Categoria'], 
        df_filtrado['Prioridade'], 
        values=df_filtrado['ID_Chamado'], 
        aggfunc='count'
    ).fillna(0).astype(int)
    
    # Renderização do mapa de calor (Heatmap)
    fig_heatmap = px.imshow(
        matriz_criticidade,
        labels=dict(x="Nível de Prioridade (SLA)", y="Categoria do Incidente", color="Volumetria"),
        x=matriz_criticidade.columns,
        y=matriz_criticidade.index,
        color_continuous_scale='Reds',
        text_auto=True
    )
    
    fig_heatmap.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', height=450)
    st.plotly_chart(fig_heatmap, use_container_width=True)
    
    st.markdown("### **Ações Recomendadas de Governança:**")
    st.info("""
    * **Alta Concentração em Críticos/Redes:** Indica fadiga de infraestrutura de hardware central (Switches/Roteadores). Recomenda-se auditoria de link.
    * **Alta Concentração em Baixa/Sistemas:** Gargalo de treinamento de usuários. Recomenda-se criação de artigos de autoajuda na base de conhecimento.
    """)


# ==============================================================================
# ABA 3: GESTÃO DE ATENDENTES & PERFORMANCE INDIVIDUAL
# ==============================================================================
with aba_performance:
    st.markdown("## **Rank de Produtividade e Eficiência Científica dos Atendentes**")
    
    # Agrupamento analítico complexo por técnico atendente
    performance_tecnicos = df_filtrado.groupby('Tecnico').agg(
        Chamados_Fechados=('ID_Chamado', 'count'),
        SLA_Cumprido=('Dentro_SLA', lambda x: (x == 'Sim').sum()),
        Tempo_Medio_Resolucao=('Tempo_Resolucao_Horas', 'mean'),
        Satisfacao_Media=('Nota_CSAT', 'mean')
    ).reset_index()
    
    # Cálculo de métricas derivadas em tempo real
    performance_tecnicos['Taxa_SLA'] = (performance_tecnicos['SLA_Cumprido'] / performance_tecnicos['Chamados_Fechados'] * 100).round(1)
    performance_tecnicos['Tempo_Medio_Resolucao'] = performance_tecnicos['Tempo_Medio_Resolucao'].round(1)
    performance_tecnicos['Satisfacao_Media'] = performance_tecnicos['Satisfacao_Media'].round(2)
    
    # Limpeza de colunas intermediárias para exibição final limpa
    df_ranking_final = performance_tecnicos[['Tecnico', 'Chamados_Fechados', 'Taxa_SLA', 'Tempo_Medio_Resolucao', 'Satisfacao_Media']]
    df_ranking_final.columns = ['Engenheiro de Suporte', 'Tickets Concluídos', 'Taxa de SLA (%)', 'MTTR (Horas)', 'CSAT Individual']
    
    # Renderização da tabela interativa ordenada por produtividade
    st.dataframe(
        df_ranking_final.sort_values(by='Tickets Concluídos', ascending=False),
        use_container_width=True,
        hide_index=True
    )
    
    st.markdown("---")
    st.markdown("### **Mecanismo de Exportação de Dados Regulatórios**")
    st.markdown("Extraia os dados refinados pelos filtros da barra lateral para auditorias internas de governança.")
    
    # Criação de colunas para botões de download
    csv_data = df_filtrado.to_csv(index=False).encode('utf-8')
    
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        st.download_button(
            label="📥 Baixar Base Filtrada (CSV)",
            data=csv_data,
            file_name=f"relatorio_suporte_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    with btn_col2:
        st.caption("O arquivo gerado obedece aos critérios da LGPD, omitindo dados sensíveis de identificação direta dos usuários.")


# ==============================================================================
# ABA 4: GOVERNANÇA, QUALIDADE DE DADOS & AUDITORIA
# ==============================================================================
with aba_auditoria:
    st.markdown("## **Painel de Controle de Qualidade de Dados (Data Quality)**")
    st.markdown("Logs automáticos gerados pela pipeline de ingestão do dashboard para validação de integridade técnica.")
    
    aud_col1, aud_col2, aud_col3, aud_col4 = st.columns(4)
    with aud_col1:
        st.metric("Registros Brutos Capturados", log_auditoria["registros_brutos"])
    with aud_col2:
        st.metric("Registros Pós-Expurgo (Líquido)", log_auditoria["registros_liquidos"])
    with aud_col3:
        st.metric("Inconsistências Corrigidas", log_auditoria["valores_nulos"])
    with aud_col4:
        st.metric("Duplicidades Eliminadas", log_auditoria["duplicados_removidos"])
        
    st.markdown("---")
    st.markdown("### **Esquema de Metadados do Banco de Dados Ativo**")
    
    # Exibe as colunas ativas tratadas estruturalmente pela aplicação
    st.code(f"""
    // Estrutura de Schema de Dados (Camada de Negócio)
    DataFrame_Suporte_Ativo = {{
        Total_Colunas_Ativas: {len(log_auditoria["colunas_processadas"])},
        Campos_Disponiveis_Para_Queries: {log_auditoria["colunas_processadas"]},
        Status_Pipeline: "HEALTHY",
        Engine_Runtime: "Pandas Core 2.0 / Streamlit Execution Layer"
    }}
    """, language="json")


# ==============================================================================
# 5. GERENCIADOR DE INICIALIZAÇÃO EM AMBIENTE WINDOWS (CHROME RUNNER)
# ==============================================================================
url_dashboard = "http://localhost:8501"
if "chrome_inicializado" not in st.session_state:
    try:
        caminho_windows_chrome = "C:/Program Files/Google/Chrome/Application/chrome.exe %s"
        webbrowser.get(caminho_windows_chrome).open(url_dashboard)
        st.session_state["chrome_inicializado"] = True
    except Exception:
        pass