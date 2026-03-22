import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
}


def baixar_pagina(url):
    resposta = requests.get(url, headers=HEADERS, timeout=20)
    resposta.raise_for_status()
    return resposta.text


def extrair_texto(elemento):
    if elemento:
        return elemento.get_text(strip=True)
    return ""


def converter_preco(texto_preco):
    if not texto_preco:
        return None

    texto_preco = texto_preco.replace(".", "").replace(",", "").strip()

    try:
        return float(texto_preco)
    except ValueError:
        return None


def coletar_produtos(html):
    soup = BeautifulSoup(html, "html.parser")
    produtos = []

    cards = soup.select(".ui-search-layout__item")

    if not cards:
        cards = soup.select(".ui-search-result")

    if not cards:
        cards = soup.select("li.ui-search-layout__item")

    print("Quantidade de cards encontrados:", len(cards))
    print("Título da página:", soup.title.get_text(strip=True) if soup.title else "Sem título")

    for card in cards:
        titulo = (
            extrair_texto(card.select_one(".poly-component__title")) or
            extrair_texto(card.select_one(".ui-search-item__title")) or
            extrair_texto(card.select_one("h2")) or
            extrair_texto(card.select_one("h3"))
        )

        preco_texto = (
            extrair_texto(card.select_one(".andes-money-amount__fraction")) or
            extrair_texto(card.select_one(".price-tag-fraction"))
        )

        preco = converter_preco(preco_texto)

        link_elemento = (
            card.select_one("a.poly-component__title") or
            card.select_one("a.ui-search-link") or
            card.select_one("a")
        )

        link = link_elemento.get("href") if link_elemento else ""

        vendedor = (
            extrair_texto(card.select_one(".poly-component__seller")) or
            extrair_texto(card.select_one(".ui-search-official-store-label")) or
            ""
        )

        if titulo and preco is not None:
            produtos.append({
                "titulo": titulo,
                "preco": preco,
                "vendedor": vendedor,
                "link": link
            })

    return produtos