import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(
    page_title="HortaSense | Monitoramento IoT",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

NAVY = "#022859"
BLUE = "#035AA6"
CYAN = "#049DBF"
AQUA = "#1DDDF2"

st.markdown(f"""
<style>
    .stApp {{ background: #F4F7FB; }}
    [data-testid="stSidebar"] {{ background: {NAVY}; }}
    [data-testid="stSidebar"] * {{ color: white !important; }}
    .hero {{
        background: linear-gradient(120deg, {NAVY}, {BLUE});
        padding: 2rem 2.2rem; border-radius: 18px; color: white;
        margin-bottom: 1.2rem;
    }}
    .hero h1 {{ color: white; margin: 0; font-size: 2.25rem; }}
    .hero p {{ color: #DCEBFA; margin-bottom: 0; font-size: 1.05rem; }}
    .small-note {{ color: #607086; font-size: .88rem; }}
    div[data-testid="stMetric"] {{
        background: white; padding: 1rem; border-radius: 12px;
        border: 1px solid #E4EAF2;
    }}
    h2, h3 {{ color: {NAVY}; }}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    csv_path = Path(__file__).parent / "base_hortinha.csv"
    raw = pd.read_csv(csv_path, sep=None, engine="python", encoding="utf-8-sig")
    raw.columns = [str(c).replace("\\ufeff", "").strip() for c in raw.columns]
    required = ["data_hora", "umidade_percentual", "valor_adc",
                "tempo_bomba_segundos", "estado_bomba"]
    missing = [c for c in required if c not in raw.columns]
    if missing:
        raise ValueError(f"Colunas ausentes no CSV: {', '.join(missing)}")

    raw["data_hora"] = pd.to_datetime(raw["data_hora"], dayfirst=True, errors="coerce")
    for col in ["umidade_percentual", "tempo_bomba_segundos"]:
        raw[col] = pd.to_numeric(
            raw[col].astype(str).str.replace(",", ".", regex=False), errors="coerce"
        )
    raw["valor_adc"] = pd.to_numeric(raw["valor_adc"], errors="coerce")
    raw["estado_bomba"] = raw["estado_bomba"].astype(str).str.strip().str.capitalize()
    raw = raw.dropna(subset=["data_hora", "umidade_percentual", "valor_adc"])
    raw["dia"] = raw["data_hora"].dt.date
    raw["hora"] = raw["data_hora"].dt.hour
    raw["bomba_ligada"] = raw["estado_bomba"].eq("Ligada")
    return raw.sort_values("data_hora")

try:
    df = load_data()
except Exception as exc:
    st.error(f"Não foi possível carregar base_hortinha.csv: {exc}")
    st.stop()

page = st.sidebar.radio(
    "NAVEGAÇÃO",
    ["Visão geral", "O projeto", "Coleta de dados", "Banco de dados",
     "Análise dos resultados", "Conclusões"],
)
st.sidebar.markdown("---")
st.sidebar.caption("HMDC680 · Projeto Integrador Aplicado em CD & IA II")
st.sidebar.caption("Centro Universitário IESB · 2026")

start = df["data_hora"].min()
end = df["data_hora"].max()
n = len(df)
mean_h = df["umidade_percentual"].mean()
median_h = df["umidade_percentual"].median()
on_count = int(df["bomba_ligada"].sum())
pump_seconds = df["tempo_bomba_segundos"].sum()
corr = df["valor_adc"].corr(df["umidade_percentual"])

def hero(title, subtitle):
    st.markdown(
        f'<div class="hero"><h1>{title}</h1><p>{subtitle}</p></div>',
        unsafe_allow_html=True
    )

def metric_row():
    a, b, c, d = st.columns(4)
    a.metric("Leituras registradas", f"{n:,}".replace(",", "."))
    b.metric("Umidade média", f"{mean_h:.1f}%".replace(".", ","))
    c.metric("Ciclos de irrigação", "26")
    d.metric("Investimento", "R$ 248,30")

if page == "Visão geral":
    hero("HortaSense 🌱", "Sistema IoT para monitoramento e irrigação automatizada de horta doméstica")
    st.markdown(
        "Um protótipo que acompanha a umidade do solo e aciona a irrigação automaticamente "
        "quando a leitura fica abaixo do limite definido."
    )
    metric_row()
    st.subheader("O que foi desenvolvido")
    left, right = st.columns([1.15, 1])
    with left:
        st.markdown("""
        - **Monitoramento:** sensor capacitivo conectado ao ESP32.
        - **Automação:** acionamento de relé e bomba quando a umidade fica abaixo de **40%**.
        - **Registro:** armazenamento local das leituras em CSV no cartão micro SD.
        - **Banco de dados:** importação dos registros para PostgreSQL com apoio do DBeaver.
        - **Análise:** tratamento e exploração dos dados em Python, Pandas e Matplotlib.
        """)
    with right:
        st.info(
            f"**Período analisado**  \n{start:%d/%m/%Y} a {end:%d/%m/%Y}  \n\n"
            f"**Acionamentos registrados**  \n{on_count} leituras com a bomba ligada  \n\n"
            f"**Tempo total de bomba ligada**  \n{pump_seconds:.0f} segundos"
        )
    st.subheader("Umidade do solo ao longo da coleta")
    fig = px.line(df, x="data_hora", y="umidade_percentual",
                  labels={"data_hora":"Data e hora", "umidade_percentual":"Umidade (%)"},
                  color_discrete_sequence=[BLUE])
    fig.add_hline(y=40, line_dash="dash", line_color="#E07A2D",
                  annotation_text="Limite de acionamento: 40%")
    fig.update_layout(height=380, margin=dict(l=10,r=10,t=25,b=10),
                      paper_bgcolor="white", plot_bgcolor="white")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Fonte: registros do arquivo base_hortinha.csv, gerado pelo sistema embarcado.")

elif page == "O projeto":
    hero("O projeto", "Da leitura do solo à irrigação automática")
    st.subheader("Problema e proposta")
    st.write(
        "A falta de água pode prejudicar o desenvolvimento das plantas, enquanto o excesso "
        "pode desperdiçar água. O projeto propõe automatizar a irrigação de uma horta doméstica "
        "a partir da medição da umidade do solo."
    )
    st.subheader("Componentes e respectivas funções")
    components = pd.DataFrame([
        ["ESP32-WROOM-32", "Processamento, leitura do sensor e controle da automação"],
        ["Sensor capacitivo", "Medição da umidade do solo"],
        ["Módulo relé", "Chaveamento da alimentação da bomba"],
        ["Bomba submersível 12 V", "Condução da água até a planta"],
        ["Leitor e cartão micro SD", "Registro local das leituras em CSV"],
        ["Reservatório, mangueira e gotejador", "Armazenamento e condução da água"],
        ["Protoboard, jumpers e fontes", "Montagem e alimentação do circuito"],
    ], columns=["Componente", "Função"])
    st.dataframe(components, hide_index=True, use_container_width=True)
    st.subheader("Lógica de funcionamento")
    c1, c2, c3 = st.columns(3)
    c1.info("**1 · Medir**  \nO sensor fornece uma leitura analógica ao ESP32.")
    c2.info("**2 · Comparar**  \nO sistema verifica se a umidade está abaixo de 40%.")
    c3.success("**3 · Irrigar**  \nSe estiver abaixo do limite, o relé liga a bomba por 2 segundos.")
    st.warning("O relatório descreve uma leitura a cada 20 minutos. O envio ao PostgreSQL não ocorreu em tempo real.")

elif page == "Coleta de dados":
    hero("Coleta de dados", "Registros gerados pelo protótipo durante o período de operação")
    a,b,c = st.columns(3)
    a.metric("Período", f"{start:%d/%m} – {end:%d/%m/%Y}")
    b.metric("Total de registros", f"{n}")
    c.metric("Intervalo nominal", "20 minutos")
    st.write(
        "Cada linha do arquivo CSV registra data e hora, umidade percentual, valor bruto do ADC, "
        "tempo de bomba ligada e estado da bomba."
    )
    daily = df.groupby("dia").agg(
        leituras=("umidade_percentual","size"),
        umidade_media=("umidade_percentual","mean"),
        acionamentos=("bomba_ligada","sum")
    ).reset_index()
    fig = px.bar(daily, x="dia", y="leituras",
                 labels={"dia":"Dia","leituras":"Quantidade de leituras"},
                 color_discrete_sequence=[CYAN])
    fig.update_layout(height=330, paper_bgcolor="white", plot_bgcolor="white")
    st.plotly_chart(fig, use_container_width=True)
    st.subheader("Prévia dos registros")
    st.dataframe(df[["data_hora","umidade_percentual","valor_adc",
                     "tempo_bomba_segundos","estado_bomba"]].head(15),
                 hide_index=True, use_container_width=True)
    st.caption("O relatório registra lacunas na coleta, principalmente no período noturno e nos três últimos dias.")

elif page == "Banco de dados":
    hero("Armazenamento no banco de dados", "Organização dos registros para consulta e análise")
    st.subheader("Fluxo de armazenamento")
    st.code(
        "ESP32 + sensor\n"
        "      ↓\n"
        "Arquivo CSV no cartão micro SD\n"
        "      ↓\n"
        "Importação pelo DBeaver\n"
        "      ↓\n"
        "PostgreSQL · public.base_hortinha\n"
        "      ↓\n"
        "Python + Pandas · análise dos dados",
        language="text"
    )
    st.subheader("Estrutura da tabela public.base_hortinha")
    schema = pd.DataFrame([
        ["data_hora", "Data e hora da leitura"],
        ["umidade_percentual", "Umidade estimada do solo em porcentagem"],
        ["valor_adc", "Valor bruto obtido pelo conversor analógico-digital"],
        ["tempo_bomba_segundos", "Tempo de acionamento da bomba em segundos"],
        ["estado_bomba", "Estado da bomba: Ligada ou Desligada"],
    ], columns=["Coluna", "Descrição"])
    st.dataframe(schema, hide_index=True, use_container_width=True)
    st.success(
        "Segundo o relatório, os dados foram importados do cartão micro SD para a tabela "
        "public.base_hortinha em um banco PostgreSQL hospedado em servidor do IESB."
    )
    st.warning(
        "Esta apresentação utiliza o CSV fornecido como base para reproduzir a análise. "
        "Ela não abre uma conexão direta com o servidor PostgreSQL. A conexão direta exigiria "
        "credenciais protegidas e acesso de rede ao servidor."
    )

elif page == "Análise dos resultados":
    hero("Análise dos resultados", "Indicadores estatísticos e comportamento da automação")
    a,b,c,d = st.columns(4)
    a.metric("Umidade média", f"{mean_h:.1f}%".replace(".", ","))
    b.metric("Mediana", f"{median_h:.1f}%".replace(".", ","))
    c.metric("Bomba ligada", f"{on_count} leituras")
    d.metric("Tempo total ligado", f"{pump_seconds:.0f} s")
    st.subheader("Distribuição da umidade")
    fig = px.histogram(df, x="umidade_percentual", nbins=20,
                       labels={"umidade_percentual":"Umidade do solo (%)"},
                       color_discrete_sequence=[BLUE])
    fig.update_layout(height=330, paper_bgcolor="white", plot_bgcolor="white")
    st.plotly_chart(fig, use_container_width=True)
    st.subheader("Acionamentos por dia")
    daily = df.groupby("dia").agg(
        acionamentos=("bomba_ligada","sum"),
        umidade_media=("umidade_percentual","mean")
    ).reset_index()
    fig = px.bar(daily, x="dia", y="acionamentos",
                 labels={"dia":"Dia","acionamentos":"Acionamentos"},
                 color_discrete_sequence=[CYAN])
    fig.update_layout(height=330, paper_bgcolor="white", plot_bgcolor="white")
    st.plotly_chart(fig, use_container_width=True)
    st.subheader("Relação entre leitura ADC e umidade")
    fig = px.scatter(df, x="valor_adc", y="umidade_percentual",
                     labels={"valor_adc":"Valor ADC","umidade_percentual":"Umidade (%)"},
                     opacity=.65, color_discrete_sequence=[BLUE])
    fig.update_layout(height=350, paper_bgcolor="white", plot_bgcolor="white")
    st.plotly_chart(fig, use_container_width=True)
    st.metric("Correlação entre ADC e umidade", f"{corr:.3f}".replace(".", ","))
    st.caption("A correlação negativa é coerente com a calibração descrita: valores ADC maiores correspondem a solo mais seco.")
    st.subheader("Resumo diário")
    daily_display = daily.merge(
        df.groupby("dia").agg(
            leituras=("umidade_percentual","size"),
            umidade_min=("umidade_percentual","min"),
            umidade_max=("umidade_percentual","max")
        ).reset_index(), on="dia"
    )
    daily_display["umidade_media"] = daily_display["umidade_media"].round(1)
    st.dataframe(daily_display, hide_index=True, use_container_width=True)
    st.info(
        "O relatório identifica 26 ciclos de irrigação, 72 acionamentos de 2 segundos "
        "(144 segundos no total) e ganho médio de 11,2 pontos percentuais por ciclo. "
        "Ciclo e acionamento são medidas diferentes."
    )

elif page == "Conclusões":
    hero("Conclusões", "O que os dados permitem afirmar — e o que ainda precisa ser investigado")
    st.success(
        "O protótipo monitorou a umidade e acionou a bomba quando a leitura ficou abaixo de 40%, "
        "conforme a regra definida no projeto."
    )
    st.subheader("Principais resultados")
    st.markdown("""
    - Foram analisados **530 registros** ao longo de 15 dias.
    - A umidade média registrada foi de **68,4%**.
    - Foram identificados **26 ciclos de irrigação**.
    - A bomba permaneceu ligada por **144 segundos** no total.
    - O ganho médio observado foi de **11,2 pontos percentuais por ciclo**.
    - O investimento realizado foi de **R$ 248,30**.
    """)
    st.subheader("Limitações identificadas")
    st.markdown("""
    - Utilização de apenas um ponto de medição de umidade.
    - Ausência de sensores de temperatura, umidade do ar e luminosidade.
    - Lacunas e interrupção da coleta nos últimos dias.
    - Ausência de grupo de controle para medir economia de água.
    - Importação manual dos arquivos para o banco, sem API em tempo real.
    """)
    st.subheader("Trabalhos futuros")
    st.markdown("""
    - Integrar sensores DHT11 e LDR.
    - Ampliar os pontos de medição da horta.
    - Implementar uma API REST para envio direto ao PostgreSQL.
    - Comparar o consumo de água com a irrigação manual.
    """)
    st.caption("Projeto Integrador Aplicado em Ciência de Dados e Inteligência Artificial II · IESB · 2026")

st.markdown("---")
st.markdown(
    '<p class="small-note">HortaSense · Sistema IoT para Monitoramento e Irrigação Automatizada de Horta Doméstica</p>',
    unsafe_allow_html=True
)
