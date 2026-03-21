def formatar_busca(produto):
    produto = produto.strip().lower()
    produto = produto.replace(" ", "-")
    return produto