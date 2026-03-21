import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

import streamlit as st
import pandas as pd

from app.utils import formatar_busca
from app.coletor import baixar_pagina, coletar_produtos
from app.analise import (
    limpar_dados,
    analisar_precos,
    classificar_concorrencia,
    analisar_titulos,
    calcular_faixa_preco,
    detectar_oportunidade,
    calcular_score_oportunidade,
    gerar_resumo_executivo,
    calcular_preco_sugerido,
    classificar_concorrentes,
    resumo_concorrentes,
    gerar_insights,
    calcular_lucro_estimado,
    calcular_preco_minimo_lucrativo,
    calcular_faixa_ideal_mercado,
    gerar_recomendacao_venda,
    avaliar_viabilidade
)
from app.relatorio import salvar_relatorio_excel
from app.historico import salvar_historico, carregar_historico

from dashboard.componentes import card_metrica, secao_titulo, caixa_destaque
from dashboard.graficos import (
    grafico_faixa_preco,
    grafico_palavras,
    grafico_concorrentes
)

st.set_page_config(
    page_title="Marketplace Intelligence Bot",
    layout="wide"
)

st.markdown("""
<style>
    .main {
        background-color: #f5f7fb;
    }
</style>
""", unsafe_allow_html=True)


def executar_analise(produto):
    busca_formatada = formatar_busca(produto)
    url = f"https://lista.mercadolivre.com.br/{busca_formatada}"

    html = baixar_pagina(url)
    produtos = coletar_produtos(html)

    if not produtos:
        raise ValueError(
            "Nenhum produto encontrado. O site pode ter mudado a estrutura ou bloqueado a coleta."
        )

    df = pd.DataFrame(produtos)
    df = limpar_dados(df)

    if df.empty:
        raise ValueError("Os dados ficaram vazios após a limpeza.")

    resumo = analisar_precos(df)
    resumo["nivel_concorrencia"] = classificar_concorrencia(
        resumo["quantidade_produtos"]
    )
    resumo["oportunidade"] = detectar_oportunidade(resumo)

    palavras_chave = analisar_titulos(df["titulo"].tolist())
    faixa_preco = calcular_faixa_preco(df, resumo["preco_medio"])
    score_info = calcular_score_oportunidade(resumo)
    resumo_executivo = gerar_resumo_executivo(resumo, score_info)
    preco_info = calcular_preco_sugerido(df)
    faixa_ideal = calcular_faixa_ideal_mercado(df)

    df = classificar_concorrentes(df, resumo["preco_medio"])
    resumo_conc = resumo_concorrentes(df)
    insights = gerar_insights(resumo_conc)

    return {
        "df": df,
        "resumo": resumo,
        "palavras_chave": palavras_chave,
        "faixa_preco": faixa_preco,
        "score_info": score_info,
        "resumo_executivo": resumo_executivo,
        "preco_info": preco_info,
        "faixa_ideal": faixa_ideal,
        "resumo_conc": resumo_conc,
        "insights": insights
    }


st.title("📊 Marketplace Intelligence")
st.caption("Dashboard integrado ao robô de análise de mercado")

col_form1, col_form2, col_form3, col_form4 = st.columns(4)

with col_form1:
    produto = st.text_input("Produto", value="fone bluetooth")

with col_form2:
    custo_produto = st.number_input(
        "Custo do produto (R$)",
        min_value=0.0,
        value=50.0,
        step=1.0
    )

with col_form3:
    taxa_marketplace = st.number_input(
        "Taxa do marketplace (%)",
        min_value=0.0,
        value=16.0,
        step=0.5
    )

with col_form4:
    lucro_desejado = st.number_input(
        "Lucro desejado (R$)",
        min_value=0.0,
        value=20.0,
        step=1.0
    )

col_botao_1, col_botao_2 = st.columns(2)

executar = col_botao_1.button("Analisar produto", use_container_width=True)
gerar_excel = col_botao_2.button("Gerar relatório Excel", use_container_width=True)

if "resultado" not in st.session_state:
    st.session_state["resultado"] = None

if executar:
    try:
        with st.spinner("Analisando mercado, concorrência e preço sugerido..."):
            resultado = executar_analise(produto)

            salvar_historico(
                produto,
                resultado["resumo"],
                resultado["score_info"],
                resultado["preco_info"]
            )

            st.session_state["resultado"] = resultado

        st.success("Análise concluída com sucesso.")
    except Exception as erro:
        st.error(f"Erro ao analisar produto: {erro}")

resultado = st.session_state["resultado"]

if resultado:
    resumo = resultado["resumo"]
    score = resultado["score_info"]
    preco = resultado["preco_info"]

    lucro_info = calcular_lucro_estimado(
        custo_produto,
        preco["preco_sugerido"],
        taxa_marketplace
    )

    preco_minimo = calcular_preco_minimo_lucrativo(
        custo_produto,
        taxa_marketplace,
        lucro_desejado
    )

    viabilidade = avaliar_viabilidade(
        preco["preco_competitivo"],
        preco_minimo
    )

    recomendacoes = gerar_recomendacao_venda(
        resultado["resumo"],
        resultado["preco_info"],
        custo_produto
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        card_metrica("Preço Mediano", f"R$ {resumo['preco_mediano']}", "#1F4E78")

    with col2:
        card_metrica("Concorrência", resumo["nivel_concorrencia"], "#00B894")

    with col3:
        card_metrica("Score", score["score"], "#FDCB6E")

    with col4:
        card_metrica("Preço Competitivo", f"R$ {preco['preco_competitivo']}", "#E84393")

    secao_titulo("🎯 Faixa Ideal de Venda")

    col_fx1, col_fx2 = st.columns(2)

    with col_fx1:
        card_metrica(
            "Faixa ideal mínima",
            f"R$ {resultado['faixa_ideal']['faixa_ideal_min']}",
            "#6C5CE7"
        )

    with col_fx2:
        card_metrica(
            "Faixa ideal máxima",
            f"R$ {resultado['faixa_ideal']['faixa_ideal_max']}",
            "#00CEC9"
        )

    secao_titulo("💰 Estratégias de Preço")

    col_preco1, col_preco2, col_preco3 = st.columns(3)

    with col_preco1:
        card_metrica("Preço agressivo", f"R$ {preco['preco_agressivo']}", "#D63031")

    with col_preco2:
        card_metrica("Preço competitivo", f"R$ {preco['preco_competitivo']}", "#0984E3")

    with col_preco3:
        card_metrica("Preço premium", f"R$ {preco['preco_premium']}", "#00B894")

    secao_titulo("💰 Viabilidade Financeira")

    col_fin1, col_fin2, col_fin3, col_fin4 = st.columns(4)

    with col_fin1:
        card_metrica("Taxa estimada", f"R$ {lucro_info['taxa_valor']}", "#6C5CE7")

    with col_fin2:
        card_metrica("Lucro estimado", f"R$ {lucro_info['lucro_estimado']}", "#00CEC9")

    with col_fin3:
        card_metrica("Margem estimada", f"{lucro_info['margem_estimada']}%", "#0984E3")

    with col_fin4:
        card_metrica("Preço mínimo lucrativo", f"R$ {preco_minimo}", "#E17055")

    st.markdown("---")
    secao_titulo("✅ Vale a Pena Vender?")

    if viabilidade["status"] == "vale_muito":
        caixa_destaque(
            f"{viabilidade['mensagem']} Diferença positiva: R$ {viabilidade['diferenca']}",
            "#eafaf1",
            "#00B894",
            "#1a1a1a"
        )
    elif viabilidade["status"] == "vale_apertado":
        caixa_destaque(
            f"{viabilidade['mensagem']} Diferença positiva: R$ {viabilidade['diferenca']}",
            "#fff8e8",
            "#FDCB6E",
            "#1a1a1a"
        )
    else:
        caixa_destaque(
            f"{viabilidade['mensagem']} Diferença: R$ {viabilidade['diferenca']}",
            "#fdecec",
            "#D63031",
            "#1a1a1a"
        )

    st.markdown("---")
    secao_titulo("📈 Análise de Dados")

    df_faixa = pd.DataFrame(
        list(resultado["faixa_preco"].items()),
        columns=["faixa", "quantidade"]
    )

    df_palavras = pd.DataFrame(
        resultado["palavras_chave"],
        columns=["palavra", "frequencia"]
    )

    df_concorrentes = pd.DataFrame(
        list(resultado["resumo_conc"].items()),
        columns=["tipo_concorrente", "quantidade"]
    )

    col_esq, col_dir = st.columns([2, 1])

    with col_esq:
        st.plotly_chart(
            grafico_faixa_preco(df_faixa),
            use_container_width=True
        )

        st.plotly_chart(
            grafico_palavras(df_palavras),
            use_container_width=True
        )

    with col_dir:
        st.plotly_chart(
            grafico_concorrentes(df_concorrentes),
            use_container_width=True
        )

    st.markdown("---")
    secao_titulo("🛒 Recomendação para o Vendedor")

    for rec in recomendacoes:
        caixa_destaque(rec, "#eefaf0", "#00B894", "#1a1a1a")

    st.markdown("---")
    secao_titulo("🧾 Resumo Executivo")
    caixa_destaque(resultado["resumo_executivo"], "#eef5ff", "#1F4E78", "#1a1a1a")

    st.markdown("---")
    secao_titulo("💡 Insights de Mercado")

    for insight in resultado["insights"]:
        caixa_destaque(insight, "#fff8e8", "#FDCB6E", "#1a1a1a")

    st.markdown("---")
    secao_titulo("📦 Produtos Coletados")
    st.dataframe(resultado["df"], use_container_width=True)

    st.markdown("---")
    secao_titulo("🕘 Histórico de Análises")

    historico = carregar_historico()
    if not historico.empty:
        st.dataframe(historico, use_container_width=True)
    else:
        st.info("Nenhuma análise salva ainda.")

    if gerar_excel:
        try:
            salvar_relatorio_excel(
                resultado["df"],
                resultado["resumo"],
                resultado["palavras_chave"],
                resultado["faixa_preco"],
                resultado["score_info"],
                resultado["resumo_executivo"],
                resultado["preco_info"],
                resultado["resumo_conc"],
                resultado["insights"]
            )
            st.success("Relatório Excel gerado com sucesso em data/relatorio_marketplace.xlsx")
        except Exception as erro:
            st.error(f"Erro ao gerar Excel: {erro}")