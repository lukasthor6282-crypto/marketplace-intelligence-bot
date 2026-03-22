import time
import random
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,*/*;q=0.8"
    ),
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
}

SESSION = requests.Session()
SESSION.headers.update(HEADERS)


def formatar_busca_url(produto: str) -> str:
    return quote_plus(produto.strip())


def baixar_pagina(produto: str) -> str:
    busca = formatar_busca_url(produto)
    url = f"https://lista.mercadolivre.com.br/{busca}"

    time.sleep(random.uniform(1.0, 2.2))

    resposta = SESSION.get(url, timeout=25, allow_redirects=True)
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


def pagina_parece_bloqueada(html: str) -> bool:
    html_lower = html.lower()

    sinais_fortes = [
        "captcha",
        "access denied",
        "are you a human",
        "security check",
        "/captcha/",
    ]

    return any(sinal in html_lower for sinal in sinais_fortes)


def coletar_produtos(html):
    soup = BeautifulSoup(html, "html.parser")
    produtos = []

    # Só bloqueia se os sinais forem muito claros
    if pagina_parece_bloqueada(html):
        titulo = soup.title.get_text(strip=True) if soup.title else "Sem título"
        raise ValueError(f"O site retornou possível bloqueio. Título da página: {titulo}")

    seletores_cards = [
        ".ui-search-layout__item",
        ".ui-search-result",
        ".poly-card",
        "li.ui-search-layout__item",
        "ol.ui-search-layout li",
        "div[data-testid='product-card']",
    ]

    cards = []
    for seletor in seletores_cards:
        cards = soup.select(seletor)
        if cards:
            break

    # Fallback mais amplo
    if not cards:
        cards = soup.find_all(["li", "div"], limit=300)

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

    # remove duplicados
    produtos_unicos = []
    vistos = set()

    for produto in produtos:
        chave = (produto["titulo"], produto["preco"])
        if chave not in vistos:
            vistos.add(chave)
            produtos_unicos.append(produto)

    if not produtos_unicos:
        titulo = soup.title.get_text(strip=True) if soup.title else "Sem título"
        trecho = soup.get_text(separator=" ", strip=True)[:500]
        raise ValueError(
            f"Nenhum produto encontrado. Título da página: {titulo}. Conteúdo inicial: {trecho}"
        )

    return produtos_unicos