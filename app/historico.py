import os
import pandas as pd


ARQUIVO_HISTORICO = "data/historico_analises.csv"


def salvar_historico(produto, resumo, score_info, preco_info):
    novo_registro = pd.DataFrame([{
        "produto": produto,
        "quantidade_produtos": resumo["quantidade_produtos"],
        "preco_medio": resumo["preco_medio"],
        "menor_preco": resumo["menor_preco"],
        "maior_preco": resumo["maior_preco"],
        "nivel_concorrencia": resumo["nivel_concorrencia"],
        "score": score_info["score"],
        "nivel_oportunidade": score_info["nivel_oportunidade"],
        "preco_sugerido": preco_info["preco_sugerido"],
        "estrategia_preco": preco_info["estrategia_preco"]
    }])

    if os.path.exists(ARQUIVO_HISTORICO):
        historico = pd.read_csv(ARQUIVO_HISTORICO)
        historico = pd.concat([historico, novo_registro], ignore_index=True)
    else:
        historico = novo_registro

    historico.to_csv(ARQUIVO_HISTORICO, index=False)


def carregar_historico():
    if os.path.exists(ARQUIVO_HISTORICO):
        return pd.read_csv(ARQUIVO_HISTORICO)
    return pd.DataFrame()