import re
from collections import Counter


def limpar_dados(df):
    df = df.dropna(subset=["preco", "titulo"])
    df = df[df["preco"] > 0]
    df = df.drop_duplicates(subset=["titulo", "preco"])

    df = remover_outliers_preco(df)

    return df


def analisar_precos(df):
    resumo = {
        "quantidade_produtos": len(df),
        "preco_medio": round(df["preco"].mean(), 2),
        "preco_mediano": round(df["preco"].median(), 2),
        "menor_preco": round(df["preco"].min(), 2),
        "maior_preco": round(df["preco"].max(), 2),
        "desvio_padrao": round(df["preco"].std(), 2) if len(df) > 1 else 0
    }
    return resumo


def classificar_concorrencia(qtd):
    if qtd <= 10:
        return "Baixa"
    elif qtd <= 25:
        return "Média"
    return "Alta"


def limpar_palavras(texto):
    texto = texto.lower()
    texto = re.sub(r"[^\w\s]", "", texto)

    stopwords = {
        "de", "da", "do", "das", "dos", "e", "em", "para", "com", "sem",
        "um", "uma", "o", "a", "os", "as", "no", "na", "nos", "nas",
        "por", "mais", "menos", "novo", "nova", "original",
        "kit", "ml", "mercado", "livre"
    }

    palavras = texto.split()
    palavras_filtradas = []

    for palavra in palavras:
        if palavra not in stopwords and len(palavra) > 2:
            palavras_filtradas.append(palavra)

    return palavras_filtradas


def analisar_titulos(lista_titulos, top_n=10):
    todas_palavras = []

    for titulo in lista_titulos:
        palavras = limpar_palavras(titulo)
        todas_palavras.extend(palavras)

    contador = Counter(todas_palavras)
    return contador.most_common(top_n)


def calcular_faixa_preco(df, preco_medio):
    abaixo_media = len(df[df["preco"] < preco_medio])
    acima_media = len(df[df["preco"] > preco_medio])
    iguais_media = len(df[df["preco"] == preco_medio])

    return {
        "abaixo_media": abaixo_media,
        "acima_media": acima_media,
        "iguais_media": iguais_media
    }


def detectar_oportunidade(resumo):
    qtd = resumo["quantidade_produtos"]

    if qtd <= 10:
        return "Boa oportunidade"
    elif qtd <= 25:
        return "Mercado intermediário"
    return "Mercado competitivo"


def calcular_score_oportunidade(resumo):
    score = 0

    qtd = resumo["quantidade_produtos"]
    preco_medio = resumo["preco_medio"]

    # Concorrência
    if qtd <= 10:
        score += 4
    elif qtd <= 25:
        score += 2

    # Preço médio
    if preco_medio >= 150:
        score += 3
    elif preco_medio >= 80:
        score += 2
    elif preco_medio >= 40:
        score += 1

    # Amplitude de preço
    amplitude = resumo["maior_preco"] - resumo["menor_preco"]
    if amplitude >= 100:
        score += 2
    elif amplitude >= 40:
        score += 1

    if score >= 7:
        nivel = "Alta"
    elif score >= 4:
        nivel = "Média"
    else:
        nivel = "Baixa"

    return {
        "score": score,
        "nivel_oportunidade": nivel
    }


def gerar_resumo_executivo(resumo, score_info):
    return (
        f"O mercado analisado apresentou {resumo['quantidade_produtos']} anúncios, "
        f"com preço médio de R$ {resumo['preco_medio']}, "
        f"variando de R$ {resumo['menor_preco']} até R$ {resumo['maior_preco']}. "
        f"O nível de concorrência foi classificado como {resumo['nivel_concorrencia']}. "
        f"O score final foi {score_info['score']}, "
        f"indicando {score_info['nivel_oportunidade']} oportunidade."
    )


def calcular_preco_sugerido(df):
    preco_medio = df["preco"].mean()
    preco_mediano = df["preco"].median()
    menor_preco = df["preco"].min()

    preco_agressivo = round(max(menor_preco * 0.99, preco_mediano * 0.94), 2)
    preco_competitivo = round(preco_mediano * 0.98, 2)
    preco_premium = round(preco_mediano * 1.05, 2)

    return {
        "preco_agressivo": preco_agressivo,
        "preco_competitivo": preco_competitivo,
        "preco_premium": preco_premium,
        "preco_sugerido": preco_competitivo,
        "estrategia_preco": "Competitivo"
    }

def classificar_concorrentes(df, preco_medio):
    concorrentes = []

    for _, row in df.iterrows():
        preco = row["preco"]

        if preco < preco_medio * 0.9:
            tipo = "Concorrente agressivo"
        elif preco > preco_medio * 1.1:
            tipo = "Concorrente premium"
        else:
            tipo = "Concorrente equilibrado"

        concorrentes.append(tipo)

    df["tipo_concorrente"] = concorrentes
    return df


def resumo_concorrentes(df):
    return df["tipo_concorrente"].value_counts().to_dict()


def gerar_insights(resumo_conc):
    insights = []

    if resumo_conc.get("Concorrente agressivo", 0) > 10:
        insights.append("Alta presença de concorrentes agressivos. Mercado competitivo por preço.")

    if resumo_conc.get("Concorrente premium", 0) > 5:
        insights.append("Existe espaço para posicionamento premium.")

    if resumo_conc.get("Concorrente equilibrado", 0) > 10:
        insights.append("Mercado com padrão de preço bem definido.")

    if not insights:
        insights.append("Mercado com comportamento ainda pouco definido.")

    return insights


def calcular_lucro_estimado(custo_produto, preco_venda, taxa_percentual):
    taxa_valor = preco_venda * (taxa_percentual / 100)
    lucro = preco_venda - custo_produto - taxa_valor
    margem = 0

    if preco_venda > 0:
        margem = (lucro / preco_venda) * 100

    return {
        "taxa_valor": round(taxa_valor, 2),
        "lucro_estimado": round(lucro, 2),
        "margem_estimada": round(margem, 2)
    }


def calcular_preco_minimo_lucrativo(custo_produto, taxa_percentual, lucro_desejado):
    fator = 1 - (taxa_percentual / 100)

    if fator <= 0:
        return None

    preco_minimo = (custo_produto + lucro_desejado) / fator
    return round(preco_minimo, 2)

def remover_outliers_preco(df):
    q1 = df["preco"].quantile(0.25)
    q3 = df["preco"].quantile(0.75)
    iqr = q3 - q1

    limite_inferior = q1 - 1.5 * iqr
    limite_superior = q3 + 1.5 * iqr

    df_filtrado = df[
        (df["preco"] >= limite_inferior) &
        (df["preco"] <= limite_superior)
    ].copy()

    return df_filtrado

def calcular_faixa_ideal_mercado(df):
    preco_mediano = df["preco"].median()

    faixa_min = round(preco_mediano * 0.95, 2)
    faixa_max = round(preco_mediano * 1.05, 2)

    return {
        "faixa_ideal_min": faixa_min,
        "faixa_ideal_max": faixa_max
    }

def gerar_recomendacao_venda(resumo, preco_info, custo_produto=None):
    recomendacao = []

    recomendacao.append(
        f"O preço mediano do mercado está em R$ {resumo['preco_mediano']}."
    )

    recomendacao.append(
        f"O preço competitivo sugerido é R$ {preco_info['preco_competitivo']}."
    )

    recomendacao.append(
        f"Para estratégia agressiva, o sistema sugere R$ {preco_info['preco_agressivo']}."
    )

    recomendacao.append(
        f"Para posicionamento premium, o sistema sugere R$ {preco_info['preco_premium']}."
    )

    if custo_produto is not None:
        if preco_info["preco_competitivo"] < custo_produto:
            recomendacao.append(
                "Atenção: o preço competitivo está abaixo do custo informado."
            )

    return recomendacao

def avaliar_viabilidade(preco_competitivo, preco_minimo_lucrativo):
    diferenca = round(preco_competitivo - preco_minimo_lucrativo, 2)

    if preco_minimo_lucrativo is None:
        return {
            "status": "inválido",
            "mensagem": "Não foi possível calcular o preço mínimo lucrativo.",
            "diferenca": None
        }

    if diferenca >= 15:
        return {
            "status": "vale_muito",
            "mensagem": "Vale a pena vender. Há boa margem acima do preço mínimo lucrativo.",
            "diferenca": diferenca
        }
    elif diferenca >= 0:
        return {
            "status": "vale_apertado",
            "mensagem": "Vale a pena vender, mas com margem apertada.",
            "diferenca": diferenca
        }
    else:
        return {
            "status": "nao_vale",
            "mensagem": "Não vale a pena vender nesse preço competitivo. O mercado está abaixo do seu mínimo lucrativo.",
            "diferenca": diferenca
        }