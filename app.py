
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="HortaSense",
    page_icon="🌱",
    layout="wide"
)

VERDE = "#16A34A"
VERDE_ESCURO = "#14532D"
CINZA = "#64748B"
VERMELHO = "#DC2626"

st.markdown("""
<style>
.stApp {
    background-color: #F4F7F5;
}

[data-testid="stHeader"] {
    background-color: #F4F7F5;
}

[data-testid="stMetric"] {
    background-color: #FFFFFF;
    border: 1px solid #DCE5DF;
    border-radius: 14px;
    padding: 18px;
}

[data-testid="stMetricValue"] {
    color: #14532D;
}

.hero {
    background: linear-gradient(120deg, #14532D, #15803D);
    padding: 30px;
    border-radius: 16px;
    margin-bottom: 25px;
}

.hero h1 {
    color: white;
    margin: 0;
}

.hero p {
    color: #DCFCE7;
    margin-top: 8px;
}

</style>
""", unsafe_allow_html=True)


# Carregamento e tratamento dos dados

@st.cache_data
def carregar_dados():
    caminho = Path(__file__).parent / "base_hortinha.csv"

    df = pd.read_csv(
        caminho,
        sep=";",
        encoding="utf-8-sig",
        decimal=","
    )

    df.columns = df.columns.str.strip()

    df["data_hora"] = pd.to_datetime(
        df["data_hora"],
        dayfirst=True,
        errors="coerce"
    )

    for coluna in [
        "umidade_percentual",
        "valor_adc",
        "tempo_bomba_segundos"
    ]:
        df[coluna] = pd.to_numeric(
            df[coluna].astype(str).str.replace(",", "."),
            errors="coerce"
        )

    df["estado_bomba"] = (
        df["estado_bomba"]
        .astype(str)
        .str.strip()
        .str.capitalize()
    )

    df = df.dropna(
        subset=["data_hora", "umidade_percentual", "valor_adc"]
    )

    df = df.sort_values("data_hora")

    df["dia"] = df["data_hora"].dt.date

    return df


df = carregar_dados()


# Padronização dos gráficos

def configurar_grafico(fig, altura=380):
    fig.update_layout(
        template="plotly_white",
        height=altura,
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(
            color="#243447",
            family="Arial",
            size=13
        ),
        margin=dict(l=20, r=20, t=40, b=20),
        legend_title_text=""
    )

    fig.update_xaxes(gridcolor="#EDF2EF")
    fig.update_yaxes(gridcolor="#EDF2EF")

    return fig


# Cabeçalho

def cabecalho(titulo, subtitulo):
    st.markdown(
        f"""
        <div class="hero">
            <h1>{titulo}</h1>
            <p>{subtitulo}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


# Menu lateral

st.sidebar.title("🌱 HortaSense")

st.sidebar.caption(
    "Monitoramento inteligente de hortas"
)

pagina = st.sidebar.radio(
    "Navegação",
    [
        "Visão geral",
        "O projeto",
        "Coleta de dados",
        "Banco de dados",
        "Análise dos resultados",
        "Conclusões"
    ]
)

st.sidebar.divider()

st.sidebar.markdown("### Projeto Integrador")

st.sidebar.write("Ciência de Dados e Inteligência Artificial")
st.sidebar.write("IESB | 2026")

st.sidebar.divider()


# Filtro de período

st.sidebar.markdown("### Filtros")

periodo = st.sidebar.date_input(
    "Período de análise",
    value=(df["dia"].min(), df["dia"].max()),
    min_value=df["dia"].min(),
    max_value=df["dia"].max(),
    format="DD/MM/YYYY"
)

if len(periodo) != 2:
    st.info("Selecione a data inicial e a data final.")
    st.stop()

dados = df[
    (df["dia"] >= periodo[0]) &
    (df["dia"] <= periodo[1])
].copy()

if dados.empty:
    st.info("Não existem registros nesse período.")
    st.stop()


# Indicadores

total = len(dados)

media = dados["umidade_percentual"].mean()

mediana = dados["umidade_percentual"].median()

acionamentos = int(
    (dados["estado_bomba"] == "Ligada").sum()
)

tempo_total = dados["tempo_bomba_segundos"].sum()

correlacao = dados["valor_adc"].corr(
    dados["umidade_percentual"]
)


# PÁGINA 1 — VISÃO GERAL

if pagina == "Visão geral":

    cabecalho(
        "HortaSense 🌱",
        "Sistema IoT para monitoramento e irrigação "
        "automatizada de horta doméstica"
    )

    a, b, c, d = st.columns(4)

    a.metric("Registros coletados", total)

    b.metric(
        "Umidade média",
        f"{media:.1f}%".replace(".", ",")
    )

    c.metric("Acionamentos da bomba", acionamentos)

    d.metric("Tempo de irrigação", f"{tempo_total:.0f} s")

    st.divider()

    st.subheader("Evolução da umidade do solo")

    fig = px.line(
        dados,
        x="data_hora",
        y="umidade_percentual",
        color_discrete_sequence=[VERDE],
        labels={
            "data_hora": "Data e hora",
            "umidade_percentual": "Umidade (%)"
        }
    )

    fig.update_traces(line=dict(width=2))

    fig.add_hline(
        y=40,
        line_dash="dash",
        line_color=VERMELHO,
        annotation_text="Limite de irrigação: 40%"
    )

    fig.update_yaxes(range=[0, 105])

    st.plotly_chart(
        configurar_grafico(fig, 420),
        use_container_width=True
    )

    esquerda, direita = st.columns(2)

    with esquerda:

        st.subheader("Estado da bomba")

        estados = (
            dados["estado_bomba"]
            .value_counts()
            .rename_axis("Estado")
            .reset_index(name="Quantidade")
        )

        fig = px.pie(
            estados,
            names="Estado",
            values="Quantidade",
            hole=0.65,
            color="Estado",
            color_discrete_map={
                "Ligada": VERDE,
                "Desligada": "#CBD5E1"
            }
        )

        fig.update_traces(
            textposition="inside",
            textinfo="percent"
        )

        st.plotly_chart(
            configurar_grafico(fig),
            use_container_width=True
        )

    with direita:

        st.subheader("Distribuição da umidade")

        fig = px.histogram(
            dados,
            x="umidade_percentual",
            nbins=20,
            color_discrete_sequence=[VERDE],
            labels={
                "umidade_percentual": "Umidade (%)"
            }
        )

        fig.update_yaxes(title="Quantidade de leituras")

        fig.update_layout(bargap=0.08)

        st.plotly_chart(
            configurar_grafico(fig),
            use_container_width=True
        )


# PÁGINA 2 — O PROJETO

elif pagina == "O projeto":

    cabecalho(
        "Sobre o projeto",
        "Objetivos, componentes e funcionamento"
    )

    st.subheader("Objetivo")

    st.write(
        "Desenvolver um sistema de monitoramento da "
        "umidade do solo capaz de realizar a irrigação "
        "automaticamente quando necessário."
    )

    a, b, c = st.columns(3)

    a.metric("Limite de umidade", "40%")
    b.metric("Duração da irrigação", "2 s")
    c.metric("Investimento", "R$ 248,30")

    st.subheader("Componentes utilizados")

    componentes = pd.DataFrame({
        "Componente": [
            "ESP32-WROOM-32",
            "Sensor capacitivo de umidade",
            "RTC DS3231",
            "Módulo relé",
            "Bomba submersível 12V",
            "Módulo microSD"
        ],
        "Função": [
            "Controle do sistema",
            "Monitoramento da umidade do solo",
            "Registro da data e hora",
            "Acionamento da bomba",
            "Irrigação da horta",
            "Armazenamento dos registros"
        ]
    })

    st.dataframe(
        componentes,
        hide_index=True,
        use_container_width=True
    )

    st.subheader("Funcionamento do sistema")

    a, b, c, d = st.columns(4)

    with a:
        st.markdown("### 01")
        st.markdown("**Monitoramento**")
        st.write("O sensor realiza a leitura do solo.")

    with b:
        st.markdown("### 02")
        st.markdown("**Processamento**")
        st.write("O ESP32 verifica o percentual de umidade.")

    with c:
        st.markdown("### 03")
        st.markdown("**Irrigação**")
        st.write("A bomba é acionada abaixo de 40%.")

    with d:
        st.markdown("### 04")
        st.markdown("**Armazenamento**")
        st.write("Os registros são salvos no cartão microSD.")


# PÁGINA 3 — COLETA DE DADOS

elif pagina == "Coleta de dados":

    cabecalho(
        "Coleta de dados",
        "Acompanhamento dos registros do protótipo"
    )

    a, b, c = st.columns(3)

    a.metric("Registros", total)
    b.metric("Dias com registros", dados["dia"].nunique())
    c.metric("Intervalo programado", "20 min")

    st.subheader("Quantidade de leituras por dia")

    diario = (
        dados.groupby("dia")
        .size()
        .reset_index(name="Leituras")
    )

    fig = px.bar(
        diario,
        x="dia",
        y="Leituras",
        color_discrete_sequence=[VERDE],
        text="Leituras",
        labels={"dia": "Data"}
    )

    st.plotly_chart(
        configurar_grafico(fig),
        use_container_width=True
    )

    st.subheader("Umidade média por dia")

    medias = (
        dados.groupby("dia")["umidade_percentual"]
        .mean()
        .reset_index()
    )

    fig = px.bar(
        medias,
        x="dia",
        y="umidade_percentual",
        color_discrete_sequence=[VERDE],
        labels={
            "dia": "Data",
            "umidade_percentual": "Umidade média (%)"
        }
    )

    fig.update_yaxes(range=[0, 100])

    st.plotly_chart(
        configurar_grafico(fig),
        use_container_width=True
    )


# PÁGINA 4 — BANCO DE DADOS

elif pagina == "Banco de dados":

    cabecalho(
        "Banco de dados",
        "Estrutura e registros armazenados no PostgreSQL"
    )

    st.write(
        "Os dados coletados pelo protótipo foram "
        "armazenados em CSV e posteriormente "
        "importados para o PostgreSQL pelo DBeaver."
    )

    st.subheader("Estrutura da tabela base_hortinha")

    estrutura = pd.DataFrame({
        "Campo": [
            "data_hora",
            "umidade_percentual",
            "valor_adc",
            "tempo_bomba_segundos",
            "estado_bomba"
        ],
        "Descrição": [
            "Data e hora da leitura",
            "Percentual de umidade do solo",
            "Valor registrado pelo ADC",
            "Tempo de acionamento da bomba",
            "Estado da bomba"
        ]
    })

    st.dataframe(
        estrutura,
        hide_index=True,
        use_container_width=True
    )

    st.subheader("Consultas SQL")

    st.code(
        "SELECT * FROM public.base_hortinha LIMIT 15;",
        language="sql"
    )

    st.code(
        "SELECT COUNT(*) AS total_registros "
        "FROM public.base_hortinha;",
        language="sql"
    )

    st.subheader("Registros coletados")

    estado = st.selectbox(
        "Filtrar estado da bomba",
        ["Todos", "Ligada", "Desligada"]
    )

    tabela = dados.copy()

    if estado != "Todos":
        tabela = tabela[tabela["estado_bomba"] == estado]

    tabela = tabela.drop(columns=["dia"])

    st.dataframe(
        tabela,
        hide_index=True,
        use_container_width=True
    )

    st.download_button(
        "Baixar dados em CSV",
        data=tabela.to_csv(
            index=False,
            sep=";",
            decimal=","
        ).encode("utf-8-sig"),
        file_name="hortasense_dados.csv",
        mime="text/csv"
    )


# PÁGINA 5 — ANÁLISE DOS RESULTADOS

elif pagina == "Análise dos resultados":

    cabecalho(
        "Análise dos resultados",
        "Estatísticas e comportamento da irrigação"
    )

    a, b, c, d = st.columns(4)

    a.metric("Umidade média", f"{media:.1f}%")
    b.metric("Mediana", f"{mediana:.1f}%")
    c.metric("Acionamentos", acionamentos)

    d.metric(
        "Correlação ADC",
        f"{correlacao:.3f}" if pd.notna(correlacao) else "N/D"
    )

    st.subheader("Relação entre ADC e umidade")

    fig = px.scatter(
        dados,
        x="valor_adc",
        y="umidade_percentual",
        color_discrete_sequence=[VERDE],
        labels={
            "valor_adc": "Valor ADC",
            "umidade_percentual": "Umidade (%)"
        }
    )

    st.plotly_chart(
        configurar_grafico(fig),
        use_container_width=True
    )

    st.caption(
        "Quanto maior o valor ADC, menor a umidade indicada."
    )

    st.subheader("Acionamentos da bomba por dia")

    bomba = dados.assign(
        acionamento=dados["estado_bomba"].eq("Ligada")
    )

    bomba = (
        bomba.groupby("dia")["acionamento"]
        .sum()
        .reset_index()
    )

    fig = px.bar(
        bomba,
        x="dia",
        y="acionamento",
        text="acionamento",
        color_discrete_sequence=[VERDE],
        labels={
            "dia": "Data",
            "acionamento": "Acionamentos"
        }
    )

    st.plotly_chart(
        configurar_grafico(fig),
        use_container_width=True
    )

    st.subheader("Umidade por estado da bomba")

    fig = px.box(
        dados,
        x="estado_bomba",
        y="umidade_percentual",
        color="estado_bomba",
        color_discrete_map={
            "Ligada": VERDE,
            "Desligada": CINZA
        },
        labels={
            "estado_bomba": "Estado da bomba",
            "umidade_percentual": "Umidade (%)"
        }
    )

    fig.add_hline(
        y=40,
        line_dash="dash",
        line_color=VERMELHO
    )

    st.plotly_chart(
        configurar_grafico(fig),
        use_container_width=True
    )


# PÁGINA 6 — CONCLUSÕES

elif pagina == "Conclusões":

    cabecalho(
        "Conclusões",
        "Resultados alcançados e melhorias futuras"
    )

    st.subheader("Resultados alcançados")

    st.markdown("""
    - Monitoramento automatizado da umidade do solo.
    - Acionamento da irrigação conforme a umidade registrada.
    - Armazenamento dos dados coletados.
    - Organização dos registros no PostgreSQL.
    - Desenvolvimento de um dashboard interativo.
    """)

    st.subheader("Limitações")

    st.markdown("""
    - Interrupções durante o período de coleta.
    - Utilização de apenas um sensor de umidade.
    - Ausência de monitoramento em tempo real.
    - Ausência de comparação com a irrigação manual.
    """)

    st.subheader("Melhorias futuras")

    st.markdown("""
    - Inclusão de sensores de temperatura e luminosidade.
    - Implementação da comunicação por API.
    - Monitoramento em tempo real.
    - Ampliação da quantidade de sensores.
    - Avaliação do consumo de água.
    """)

    st.success(
        "O projeto demonstrou a aplicação da Internet "
        "das Coisas e da Ciência de Dados no "
        "monitoramento de uma horta doméstica."
    )


# Rodapé

st.divider()

st.caption(
    "HortaSense | Projeto Integrador HMDC680 | "
    "Ciência de Dados e Inteligência Artificial | IESB 2026"
)
