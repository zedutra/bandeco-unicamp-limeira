import argparse
from datetime import datetime, timedelta
import json
import os
import sys
from typing import Dict, Optional
from bs4 import BeautifulSoup
import requests

URL_CARDAPIO = "https://www.sar.unicamp.br/RU/view/site/cardapio.php"
HEADERS_PADRAO = {
    "Host": "www.sar.unicamp.br",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
}

CHAVES_REFEICAO = (
    "Acompanhamentos",
    "Prato Principal",
    "Guarnição",
    "Salada",
    "Sobremesa",
    "Refresco",
    "Extra",
    "Nota Técnica",
)
CHAVES_CAFE = ("Comida", "Bebida")

COR_RESET = "\033[0m"
COR_TITULO = "\033[1;36m"
COR_CHAVE = "\033[1;33m"
COR_NOTA = "\033[0;31m"

CardapioDict = Dict[str, Dict[str, Optional[str]]]


def formatar_string(string: str) -> str:
    """Remove espaços extras e extrai o valor após o primeiro ':' se existir."""
    palavras = string.split()
    string_limpa = " ".join(palavras)
    if ":" in string_limpa:
        _, valor = string_limpa.split(":", 1)
        return valor.strip()
    return string_limpa


def criar_parser() -> argparse.ArgumentParser:
    """Configura e retorna o parser de argumentos de linha de comando."""
    parser = argparse.ArgumentParser(
        description="Programa para verificar o cardápio do restaurante universitário da Unicamp de Limeira"
    )
    parser.add_argument(
        "-v", "-vegano", "--vegano", dest="v", action="store_true", help="Filtra pelas refeições veganas"
    )
    parser.add_argument(
        "-p", "-padrao", "--padrao", dest="p", action="store_true", help="Filtra pelas refeições padrão"
    )
    parser.add_argument(
        "-a", "-almoco", "--almoco", dest="a", action="store_true", help="Requisita o cardápio do almoço"
    )
    parser.add_argument(
        "-j", "-jantar", "--jantar", dest="j", action="store_true", help="Requisita o cardápio do jantar"
    )
    parser.add_argument(
        "-c", "-cafe", "--cafe", dest="c", action="store_true", help="Requisita o cardápio do café da manhã"
    )

    grupo_data = parser.add_mutually_exclusive_group()
    grupo_data.add_argument("--data", type=str, help="Data no formato dd-mm-yyyy")
    grupo_data.add_argument(
        "-m", "--amanha", action="store_true", help="Requisita o cardápio de amanhã"
    )
    grupo_data.add_argument(
        "-o", "--ontem", action="store_true", help="Requisita o cardápio de ontem"
    )

    parser.add_argument(
        "--json", action="store_true", help="Exibe o cardápio em formato JSON"
    )
    parser.add_argument(
        "--sem-cor", action="store_true", help="Desativa a formatação colorida no terminal"
    )
    return parser


def resolver_data(
    data_str: Optional[str] = None,
    amanha: bool = False,
    ontem: bool = False,
    referencia: Optional[datetime] = None,
) -> str:
    """Converte a data informada (dd-mm-yyyy) ou atalhos para o formato da API (yyyy-mm-dd)."""
    base = referencia or datetime.now()
    if data_str:
        try:
            data = datetime.strptime(data_str, "%d-%m-%Y")
            return data.strftime("%Y-%m-%d")
        except ValueError as exc:
            raise ValueError("Formato de data inválido. Use o formato dd-mm-yyyy.") from exc
    if amanha:
        return (base + timedelta(days=1)).strftime("%Y-%m-%d")
    if ontem:
        return (base - timedelta(days=1)).strftime("%Y-%m-%d")
    return base.strftime("%Y-%m-%d")


def requisitar_html_cardapio(data: str, timeout: int = 10) -> str:
    """Faz a requisição HTTP POST ao site da SAR Unicamp e retorna o HTML."""
    response = requests.post(
        URL_CARDAPIO,
        headers=HEADERS_PADRAO,
        data={"data": data},
        timeout=timeout,
    )
    response.raise_for_status()
    return response.text


def extrair_cardapio(html: str) -> CardapioDict:
    """Extrai as tabelas de refeições do HTML e retorna um dicionário estruturado."""
    site = BeautifulSoup(html, "html.parser")
    tables = site.find_all("table")
    if len(tables) < 5:
        return {}

    definicoes_refeicoes = (
        ("Almoço Padrão", CHAVES_REFEICAO),
        ("Almoço Vegano", CHAVES_REFEICAO),
        ("Jantar Padrão", CHAVES_REFEICAO),
        ("Jantar Vegano", CHAVES_REFEICAO),
        ("Café da Manhã", CHAVES_CAFE),
    )

    cardapio: CardapioDict = {}
    for indice, (nome_refeicao, chaves) in enumerate(definicoes_refeicoes):
        dados_refeicao: Dict[str, Optional[str]] = dict.fromkeys(chaves)
        td_comidas = tables[indice].find_all("td")
        for chave, td in zip(chaves, td_comidas):
            dados_refeicao[chave] = formatar_string(td.get_text())
        cardapio[nome_refeicao] = dados_refeicao

    return cardapio


def remover_refeicao(refeicao: str, cardapio: CardapioDict) -> CardapioDict:
    """Remove uma refeição do dicionário do cardápio, caso exista."""
    cardapio.pop(refeicao, None)
    return cardapio


def filtrar_cardapio(
    cardapio_completo: CardapioDict,
    almoco: bool = False,
    jantar: bool = False,
    cafe: bool = False,
    vegano: bool = False,
    padrao: bool = False,
) -> CardapioDict:
    """Filtra o cardápio completo de acordo com as opções escolhidas pelo usuário."""
    if not cardapio_completo:
        return {}

    todas_refeicoes = not (almoco or jantar or cafe)
    cardapio: CardapioDict = {}

    if almoco or todas_refeicoes:
        if "Almoço Padrão" in cardapio_completo:
            cardapio["Almoço Padrão"] = cardapio_completo["Almoço Padrão"]
        if "Almoço Vegano" in cardapio_completo:
            cardapio["Almoço Vegano"] = cardapio_completo["Almoço Vegano"]

    if jantar or todas_refeicoes:
        if "Jantar Padrão" in cardapio_completo:
            cardapio["Jantar Padrão"] = cardapio_completo["Jantar Padrão"]
        if "Jantar Vegano" in cardapio_completo:
            cardapio["Jantar Vegano"] = cardapio_completo["Jantar Vegano"]

    if cafe or todas_refeicoes:
        if "Café da Manhã" in cardapio_completo:
            cardapio["Café da Manhã"] = cardapio_completo["Café da Manhã"]

    if vegano and not padrao:
        remover_refeicao("Almoço Padrão", cardapio)
        remover_refeicao("Jantar Padrão", cardapio)
    elif padrao and not vegano:
        remover_refeicao("Almoço Vegano", cardapio)
        remover_refeicao("Jantar Vegano", cardapio)

    return cardapio


def suporta_cores(sem_cor: bool = False) -> bool:
    """Verifica se o terminal atual suporta cores ANSI."""
    if sem_cor or os.environ.get("NO_COLOR"):
        return False
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def imprimir_cardapio(
    cardapio: CardapioDict,
    formato_json: bool = False,
    usar_cores: bool = False,
) -> None:
    """Exibe o cardápio formatado no terminal ou em JSON."""
    if formato_json:
        print(json.dumps(cardapio, ensure_ascii=False, indent=2))
        return

    if not cardapio:
        print("Nenhuma refeição encontrada para os filtros selecionados.")
        return

    itens_refeicao = list(cardapio.items())
    for idx, (chave, valor) in enumerate(itens_refeicao):
        if usar_cores:
            print(f"{COR_TITULO}{chave}:{COR_RESET}")
        else:
            print(f"{chave}:")

        for sub_chave, sub_valor in valor.items():
            texto_valor = sub_valor if sub_valor is not None else "Não informado"
            if usar_cores:
                cor_item = COR_NOTA if sub_chave == "Nota Técnica" else COR_CHAVE
                print(f"  {cor_item}{sub_chave}:{COR_RESET} {texto_valor}")
            else:
                print(f"  {sub_chave}: {texto_valor}")

        if idx < len(itens_refeicao) - 1:
            print()


def main() -> None:
    parser = criar_parser()
    args = parser.parse_args()

    try:
        data = resolver_data(args.data, amanha=args.amanha, ontem=args.ontem)
    except ValueError as erro:
        print(str(erro), file=sys.stderr)
        sys.exit(1)

    try:
        html = requisitar_html_cardapio(data)
    except requests.RequestException as erro:
        print("Não foi possível obter informações do cardápio.", file=sys.stderr)
        print(f"Erro: {erro}", file=sys.stderr)
        sys.exit(1)

    cardapio_completo = extrair_cardapio(html)
    if not cardapio_completo:
        if args.json:
            print(json.dumps({}, ensure_ascii=False))
        else:
            print(f"Não há cardápio cadastrado para a data {data}.")
        sys.exit(0)

    cardapio_filtrado = filtrar_cardapio(
        cardapio_completo,
        almoco=args.a,
        jantar=args.j,
        cafe=args.c,
        vegano=args.v,
        padrao=args.p,
    )
    imprimir_cardapio(
        cardapio_filtrado,
        formato_json=args.json,
        usar_cores=suporta_cores(args.sem_cor),
    )


if __name__ == "__main__":
    main()