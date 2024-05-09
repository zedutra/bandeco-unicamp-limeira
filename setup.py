import requests
from bs4 import BeautifulSoup
import argparse
from datetime import datetime

# Funcao para limpar espacos extras nas strings
def formatar_string(string):
    # Divide a string em palavras
    palavras = string.split()

    # Une as palavras novamente com um único espaço entre elas
    string_limpa = ' '.join(palavras)
    # Tenta dividir a string por : para pegar apenas o nome do alimento (ACOMPANHAMENTOS:ARROZ E FEIJÃO)
    try:
        string_dividida = string_limpa.split(':')
        string_formatada = string_dividida[1].strip()
        return string_formatada
    except:
        return string_limpa

# Imprime o cardapio
def imprimir_cardapio(cardapio):
    for chave, valor in cardapio.items():
        print(f"{chave}:")
        for sub_chave, sub_valor in valor.items():
            print(f"  {sub_chave}: {sub_valor}")

# Se existir a refeicao do cardapio, remove
def remover_refeicao(refeicao, cardapio):
    if refeicao in cardapio:
        cardapio.pop(refeicao)
    return cardapio

def main():
    # Tratando os argumentos
    parser = argparse.ArgumentParser(description='Programa para verificar o cardapio do restaurante universitario da Unicamp de Limeira')
    parser.add_argument('-v', '-vegano', action='store_true', help='Filtra pelas refeições veganas')
    parser.add_argument('-p', '-padrao', action='store_true', help='Filtra pelas refeições padrão')
    parser.add_argument('-a', '-almoco', action='store_true', help='Requisita o cardápio do almoço')
    parser.add_argument('-j', '-jantar', action='store_true', help='Requisita o cardápio do jantar')
    parser.add_argument('-c', '-cafe', action='store_true', help='Requisita o cardápio do café da manhã')
    parser.add_argument('--data', type=str, help='Data no formato dd-mm-yyyy')
    args = parser.parse_args()
    # Verificando se existem argumentos de refeicao
    if args.a or args.j or args.c:
        no_args = False
    else:
        no_args = True

    # URL alvo
    url = "https://www.sar.unicamp.br/RU/view/site/cardapio.php"

    # Data a ser requisitada do cardápio
    if args.data:
        try:
            data = datetime.strptime(args.data, '%d-%m-%Y')
            data = data.strftime('%Y-%m-%d')
        except ValueError:
            print("Formato de data inválido. Use o formato dd-mm-yyyy.")
            exit()
    else:
        data = datetime.now().strftime('%Y-%m-%d')

    payload = {
        'data': data
    }

    # Headers da requisicao
    headers = {
        "Host": "www.sar.unicamp.br",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    }

    # Enviando a requisicao e verificando erros
    try:
        response = requests.post(url, headers=headers, data=payload)
        if response.status_code != 200:
            print('Não foi possível obter informações do cardápio')
            print(f'Error: {response.status_code}')
            exit()
    except Exception as e:
        print('Não foi possível obter informações do cardápio')
        exit()

    site = BeautifulSoup(response.text, "html.parser")

    # Procurando as tabelas de cada refeicao
    tables = site.find_all("table")

    # Chaves de cada refeicao e cafe
    refeicao_keys = ('Acompanhamentos', 'Prato Principal', 'Guarnição', 'Salada', 'Sobremesa', 'Refresco', 'Extra', 'Nota Técnica')
    cafe_keys = ('Comida', 'Bebida')

    # Definindo dicionarios
    almoco_padrao = dict.fromkeys(refeicao_keys)
    almoco_vegano = dict.fromkeys(refeicao_keys)
    jantar_padrao = dict.fromkeys(refeicao_keys)
    jantar_vegano = dict.fromkeys(refeicao_keys)
    cafe_manha = dict.fromkeys(cafe_keys)
    refeicoes = (almoco_padrao, almoco_vegano, jantar_padrao, jantar_vegano, cafe_manha)

    # Formatando informacoes no html para dicionarios
    for x in range(len(refeicoes)):
        td_comidas = tables[x].find_all('td')
        for td in range(len(td_comidas)):
            comida = formatar_string(td_comidas[td].getText())
            if refeicoes[x] != cafe_manha:
                refeicoes[x].update({refeicao_keys[td]: comida})
            else:
                refeicoes[x].update({cafe_keys[td]: comida})
    
    # Montando o cardapio a ser exibido
    cardapio = {}

    # Adicionando refeicoes requisitadas pelo usuario
    if args.a or no_args:
        cardapio["Almoço Padrão"] = almoco_padrao
        cardapio['Almoço Vegano'] = almoco_vegano
    if args.j or no_args:
        cardapio['Jantar Padrão'] = jantar_padrao
        cardapio['Jantar Vegano'] = jantar_vegano
    if args.c or no_args:
        cardapio['Café da Manhã'] = cafe_manha

    # Filtrando por refeicoes veganas ou padrao
    if args.v:
        cardapio = remover_refeicao('Almoço Padrão', cardapio)
        cardapio = remover_refeicao('Jantar Padrão', cardapio)
    if args.p:
        cardapio = remover_refeicao('Almoço Vegano', cardapio)
        cardapio = remover_refeicao('Jantar Vegano', cardapio)

    imprimir_cardapio(cardapio)

if __name__ == '__main__':
    main()