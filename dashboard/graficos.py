import plotly.express as px


def grafico_faixa_preco(df_faixa):
    fig = px.bar(
        df_faixa,
        x="faixa",
        y="quantidade",
        title="Distribuição de Preços",
        color_discrete_sequence=["#1F4E78"],
        text="quantidade"
    )

    fig.update_layout(
        template="plotly_white",
        title_x=0.5,
        xaxis_title="Faixa",
        yaxis_title="Quantidade",
        height=420
    )

    fig.update_traces(textposition="outside")

    return fig


def grafico_palavras(df_palavras):
    fig = px.bar(
        df_palavras,
        x="palavra",
        y="frequencia",
        title="Palavras-Chave Mais Frequentes",
        color_discrete_sequence=["#00B894"],
        text="frequencia"
    )

    fig.update_layout(
        template="plotly_white",
        title_x=0.5,
        xaxis_title="Palavra",
        yaxis_title="Frequência",
        height=420
    )

    fig.update_traces(textposition="outside")

    return fig


def grafico_concorrentes(df_concorrentes):
    fig = px.pie(
        df_concorrentes,
        names="tipo_concorrente",
        values="quantidade",
        title="Tipos de Concorrentes",
        hole=0.55,
        color_discrete_sequence=["#1F4E78", "#00B894", "#FDCB6E", "#E84393"]
    )

    fig.update_layout(
        template="plotly_white",
        title_x=0.5,
        height=420
    )

    return fig