import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="HortaSense | Apresentação do Projeto",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

NAVY = "#12345A"
BLUE = "#1769AA"
CYAN = "#159BB5"
GREEN = "#39856A"
INK = "#243447"
MUTED = "#627286"
BG = "#F5F7FA"

st.markdown(f"""
<style>
:root {{
  color-scheme: light;
}}
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {{
  background: {BG} !important;
  color: {INK} !important;
}}
[data-testid="stHeader"] {{ background: {BG} !important; }}
[data-testid="stSidebar"] {{
  background: {NAVY} !important;
}}
[data-testid="stSidebar"] * {{
  color: #FFFFFF !important;
}}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{
  color: #E6EEF7 !important;
}}
.stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown span,
[data-testid="stWidgetLabel"], [data-testid="stCaptionContainer"] {{
  color: {INK} !important;
}}
h1, h2, h3, h4 {{
  color: {NAVY} !important;
}}
[data-testid="stMetric"] {{
  background: #FFFFFF !important;
  border: 1px solid #E1E7EF !important;
  border-radius: 14px !important;
  padding: 16px 18px !important;
  box-shadow: 0 2px 8px rgba(18,52,90,.04);
}}
[data-testid="stMetricLabel"] p {{
  color: {MUTED} !important;
  font-weight: 600 !important;
}}
[data-testid="stMetricValue"] {{
  color: {NAVY} !important;
}}
.hero {{
  background: linear-gradient(115deg, {NAVY} 0%, {BLUE} 100%);
  padding: 34px 38px;
  border-radius: 18px;
  color: white !important;
  margin: 4px 0 24px 0;
}}
.hero h1 {{ color: #FFFFFF !important; margin: 0 0 8px 0; font-size: 2.2rem; }}
.hero p {{ color: #EAF2FA !important; margin: 0; font-size: 1.05rem; }}
.panel {{
  background: #FFFFFF;
  border: 1px solid #E1E7EF;
  border-radius: 14px;
  padding: 20px 22px;
}}
.step {{
  background: #FFFFFF;
  border-left: 4px solid {CYAN};
  border-radius: 10px;
  padding: 15px 18px;
  margin-bottom: 10px;
}}
div[data-testid="stAlert"] p {{ color: {INK} !important; }}
.stDataFrame {{ background: #FFFFFF; }}
small, .small-note {{ color: {MUTED} !important; }}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    path = Path(__file__).parent / "base_hortinha.csv"
    data = pd.read_csv(path, sep=None, engine="python", encoding="utf-8-sig")
    data.columns = [str(c).replace("\\ufeff", "").strip() for c in data.columns]
    required = ["data_hora", "umidade_percentual", "valor_adc",
                "tempo_bomba_segundos", "estado_bomba"]
    missing = [c for c in required if c not in data.columns]
    if missing:
        raise ValueError("Colunas não encontradas: " + ", ".join(missing))
    data["data_hora"] = pd.to_datetime(data["data_hora"], dayfirst=True, errors="coerce")
    for col in ["umidade_percentual", "tempo_bomba_segundos"]:
        data[col] = pd.to_numeric(
            data[col].astype(str).str.replace(",", ".", regex=False), errors="coerce"
        )
    data["valor_adc"] = pd.to_numeric(data["valor_adc"], errors="coerce")
    data["estado_bomba"] = data["estado_bomba"].astype(str).str.strip().str.capitalize()
    data = data.dropna(subset=["data_hora", "umidade_percentual", "valor_adc"]).copy()
    data["dia"] = data["data_hora"].dt.date
    data["bomba_ligada"] = data["estado_bomba"].eq("Ligada")
    return data.sort_values("data_hora")

try:
    df = load_data()
except Exception as e:
    st.error(f"Erro ao abrir a base de dados: {e}")
    st.stop()

periodo_inicio, periodo_fim = df.data_hora.min(), df.data_hora.max()
total = len(df)
media = df.umidade_percentual.mean()
mediana = df.umidade_percentual.median()
acionamentos = int(df.bomba_ligada.sum())
tempo_bomba = df.tempo_bomba_segundos.sum()
correlacao = df.valor_adc.corr(df.umidade_percentual)

pagina = st.sidebar.radio(
    "APRESENTAÇÃO",
    ["Visão geral", "O projeto", "Coleta de dados", "Banco de dados",
     "Análise dos resultados", "Conclusões"]
)
st.sidebar.markdown("---")
st.sidebar.markdown("**HortaSense**")
st.sidebar.caption("Projeto Integrador · HMDC680")
st.sidebar.caption("Ciência de Dados e Inteligência Artificial")
st.sidebar.caption("IESB · 2026")

def cabecalho(titulo, subtitulo):
    st.markdown(f'<div class="hero"><h1>{titulo}</h1><p>{subtitulo}</p></div>',
                unsafe_allow_html=True)

def grafico_layout(fig, altura=360):
    fig.update_layout(
        height=altura, margin=dict(l=12, r=12, t=28, b=12),
        paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
        font=dict(color=INK, family="Arial"),
        title_font=dict(color=NAVY),
    )
    fig.update_xaxes(gridcolor="#E9EEF4", zerolinecolor="#E9EEF4")
    fig.update_yaxes(gridcolor="#E9EEF4", zerolinecolor="#E9EEF4")
    return fig

if pagina == "Visão geral":
    cabecalho("HortaSense 🌱", "Sistema IoT para monitoramento e irrigação automatizada de horta doméstica")
    st.write("Um protótipo que monitora a umidade do solo e aciona a irrigação automaticamente quando necessário.")
    a, b, c, d = st.columns(4)
    a.metric("Leituras coletadas", f"{total}")
    b.metric("Umidade média", f"{media:.1f}%".replace(".", ","))
    c.metric("Ciclos de irrigação", "26")
    d.metric("Investimento realizado", "R$ 248,30")
    st.subheader("Como o sistema funciona")
    x, y = st.columns([1.1, 1])
    with x:
        st.markdown("""
        **Monitoramento**  
        Um sensor capacitivo mede a umidade do solo e envia a leitura ao ESP32.

        **Automação**  
        Quando a umidade fica abaixo de 40%, o ESP32 aciona o relé e liga a bomba por 2 segundos.

        **Registro e análise**  
        As leituras são salvas em CSV no cartão micro SD, importadas para PostgreSQL e analisadas em Python.
        """)
    with y:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown(f"**Período de coleta**  \n{periodo_inicio:%d/%m/%Y} a {periodo_fim:%d/%m/%Y}")
        st.markdown(f"**Acionamentos da bomba**  \n{acionamentos}")
        st.markdown(f"**Tempo total de bomba ligada**  \n{tempo_bomba:.0f} segundos")
        st.markdown('</div>', unsafe_allow_html=True)
    st.subheader("Variação da umidade durante a coleta")
    fig = px.line(df, x="data_hora", y="umidade_percentual",
                  labels={"data_hora":"Data e hora", "umidade_percentual":"Umidade do solo (%)"},
                  color_discrete_sequence=[BLUE])
    fig.add_hline(y=40, line_dash="dash", line_color="#D97736",
                  annotation_text="Limite de acionamento: 40%")
    st.plotly_chart(grafico_layout(fig, 390), use_container_width=True)

elif pagina == "O projeto":
    cabecalho("O projeto", "Integração entre hardware, programação, banco de dados e análise")
    st.subheader("Objetivo")
    st.write("Desenvolver um sistema IoT funcional para monitorar a umidade do solo e automatizar a irrigação de uma horta doméstica.")
    st.subheader("Componentes utilizados")
    componentes = pd.DataFrame([
        ["ESP32-WROOM-32", "Processa as leituras e controla a irrigação"],
        ["Sensor capacitivo de umidade", "Mede a umidade do solo"],
        ["Módulo relé", "Controla o acionamento da bomba"],
        ["Mini bomba submersível 12 V", "Transporta a água até a planta"],
        ["Leitor e cartão micro SD", "Armazenam localmente os registros em CSV"],
        ["Reservatório, mangueira e gotejador", "Armazenam e conduzem a água"],
        ["Protoboard, jumpers, fios e fontes", "Permitem a montagem e alimentação do circuito"],
    ], columns=["Componente", "Função"])
    st.dataframe(componentes, hide_index=True, use_container_width=True)
    st.subheader("Etapas da automação")
    st.markdown('<div class="step"><b>1. Medição</b><br>O sensor capacitivo mede a umidade do solo.</div>', unsafe_allow_html=True)
    st.markdown('<div class="step"><b>2. Decisão</b><br>O ESP32 compara o percentual de umidade com o limite de 40%.</div>', unsafe_allow_html=True)
    st.markdown('<div class="step"><b>3. Irrigação</b><br>Se a umidade estiver abaixo de 40%, o relé aciona a bomba por 2 segundos.</div>', unsafe_allow_html=True)
    st.markdown('<div class="step"><b>4. Registro</b><br>O sistema registra data, hora, umidade, valor ADC e estado da bomba no cartão micro SD.</div>', unsafe_allow_html=True)

elif pagina == "Coleta de dados":
    cabecalho("Coleta de dados", "Registros produzidos pelo protótipo durante o período de operação")
    a, b, c = st.columns(3)
    a.metric("Período", f"{periodo_inicio:%d/%m} a {periodo_fim:%d/%m/%Y}")
    b.metric("Total de registros", total)
    c.metric("Intervalo programado", "20 minutos")
    st.write("Cada registro contém data e hora, umidade percentual, valor bruto do ADC, tempo de bomba ligada e estado da bomba.")
    diario = df.groupby("dia").agg(
        leituras=("umidade_percentual", "size"),
        umidade_media=("umidade_percentual", "mean"),
        acionamentos=("bomba_ligada", "sum")
    ).reset_index()
    fig = px.bar(diario, x="dia", y="leituras",
                 labels={"dia":"Data", "leituras":"Quantidade de leituras"},
                 color_discrete_sequence=[CYAN])
    st.plotly_chart(grafico_layout(fig, 350), use_container_width=True)
    st.subheader("Amostra dos registros")
    st.dataframe(df[["data_hora", "umidade_percentual", "valor_adc",
                     "tempo_bomba_segundos", "estado_bomba"]].head(12),
                 hide_index=True, use_container_width=True)

elif pagina == "Banco de dados":
    cabecalho("Banco de dados", "Armazenamento e organização dos registros no PostgreSQL")
    st.subheader("Fluxo dos dados")
    st.markdown('<div class="step"><b>ESP32</b> · Realiza a leitura do sensor e registra os dados.</div>', unsafe_allow_html=True)
    st.markdown('<div class="step"><b>Cartão micro SD</b> · Armazena as leituras em arquivo CSV.</div>', unsafe_allow_html=True)
    st.markdown('<div class="step"><b>DBeaver</b> · Realiza a importação do arquivo para o banco.</div>', unsafe_allow_html=True)
    st.markdown('<div class="step"><b>PostgreSQL</b> · Armazena os registros na tabela <code>public.base_hortinha</code>.</div>', unsafe_allow_html=True)
    st.markdown('<div class="step"><b>Python e Pandas</b> · Permitem preparar e analisar os dados.</div>', unsafe_allow_html=True)
    st.subheader("Estrutura da tabela")
    estrutura = pd.DataFrame([
        ["data_hora", "Data e horário em que a leitura foi realizada"],
        ["umidade_percentual", "Percentual de umidade estimado pelo sensor"],
        ["valor_adc", "Valor bruto da conversão analógico-digital"],
        ["tempo_bomba_segundos", "Tempo de acionamento da bomba, em segundos"],
        ["estado_bomba", "Estado da bomba: Ligada ou Desligada"],
    ], columns=["Campo", "Conteúdo"])
    st.dataframe(estrutura, hide_index=True, use_container_width=True)
    st.markdown("**Banco:** PostgreSQL · **Tabela:** `public.base_hortinha` · **Ambiente:** servidor do IESB")
    st.caption("Os arquivos CSV foram importados para o banco após a coleta.")

elif pagina == "Análise dos resultados":
    cabecalho("Análise dos resultados", "Exploração estatística e visual dos dados coletados")
    a, b, c, d = st.columns(4)
    a.metric("Umidade média", f"{media:.1f}%".replace(".", ","))
    b.metric("Mediana", f"{mediana:.1f}%".replace(".", ","))
    c.metric("Acionamentos", acionamentos)
    d.metric("Tempo de bomba ligada", f"{tempo_bomba:.0f} s")
    st.subheader("Distribuição da umidade")
    fig = px.histogram(df, x="umidade_percentual", nbins=20,
                       labels={"umidade_percentual":"Umidade do solo (%)"},
                       color_discrete_sequence=[BLUE])
    st.plotly_chart(grafico_layout(fig, 330), use_container_width=True)
    st.subheader("Acionamentos por dia")
    diario = df.groupby("dia").agg(acionamentos=("bomba_ligada", "sum")).reset_index()
    fig = px.bar(diario, x="dia", y="acionamentos",
                 labels={"dia":"Data", "acionamentos":"Acionamentos"},
                 color_discrete_sequence=[CYAN])
    st.plotly_chart(grafico_layout(fig, 330), use_container_width=True)
    st.subheader("Relação entre valor ADC e umidade")
    fig = px.scatter(df, x="valor_adc", y="umidade_percentual",
                     labels={"valor_adc":"Valor ADC", "umidade_percentual":"Umidade (%)"},
                     opacity=.65, color_discrete_sequence=[BLUE])
    st.plotly_chart(grafico_layout(fig, 350), use_container_width=True)
    st.metric("Correlação entre ADC e umidade", f"{correlacao:.3f}".replace(".", ","))
    st.write("A correlação negativa acompanha a calibração do sensor: valores maiores de ADC representam solo mais seco.")
    st.subheader("Resumo diário")
    resumo = df.groupby("dia").agg(
        leituras=("umidade_percentual", "size"),
        umidade_media=("umidade_percentual", "mean"),
        umidade_minima=("umidade_percentual", "min"),
        umidade_maxima=("umidade_percentual", "max"),
        acionamentos=("bomba_ligada", "sum")
    ).reset_index()
    for col in ["umidade_media", "umidade_minima", "umidade_maxima"]:
        resumo[col] = resumo[col].round(1)
    st.dataframe(resumo, hide_index=True, use_container_width=True)
    st.markdown("**Resultado dos ciclos:** 26 ciclos de irrigação, 72 acionamentos de 2 segundos e ganho médio de 11,2 pontos percentuais de umidade por ciclo.")

elif pagina == "Conclusões":
    cabecalho("Conclusões", "Resultados alcançados e possibilidades de evolução")
    st.markdown("""
    O protótipo cumpriu sua finalidade de monitorar a umidade do solo e automatizar a irrigação
    com base no limite de 40%. Durante o período analisado, foram identificados 26 ciclos de
    irrigação, com ganho médio de 11,2 pontos percentuais de umidade por ciclo.
    """)
    st.subheader("Principais resultados")
    a, b, c = st.columns(3)
    a.metric("Registros analisados", total)
    b.metric("Ciclos de irrigação", "26")
    c.metric("Investimento", "R$ 248,30")
    st.subheader("Limitações identificadas")
    st.markdown("""
    - Utilização de apenas um ponto de medição de umidade.
    - Ausência de sensores de temperatura, umidade do ar e luminosidade.
    - Lacunas na coleta e interrupção nos três últimos dias.
    - Ausência de grupo de controle para quantificar a economia de água.
    - Importação dos dados por arquivo, sem envio ao banco em tempo real.
    """)
    st.subheader("Trabalhos futuros")
    st.markdown("""
    - Incluir sensores de temperatura e umidade do ar (DHT11) e luminosidade (LDR).
    - Ampliar os pontos de medição da horta.
    - Implementar uma API REST para registrar as leituras diretamente no PostgreSQL.
    - Comparar o consumo de água com a irrigação manual.
    """)
    st.markdown("**Investimento realizado:** R$ 248,30")

st.markdown("---")
st.caption("HortaSense · Projeto Integrador Aplicado em Ciência de Dados e Inteligência Artificial II · IESB · 2026")
