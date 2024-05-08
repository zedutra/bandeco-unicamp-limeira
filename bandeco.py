import requests
from bs4 import BeautifulSoup
import argparse
import re
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(description='Programa para verificar o cardápio do restaurante universitário da Unicamp de Limeira')
    parser.add_argument('-vegano', '-v', action='store_true', help='Ativa a opção vegana')
    parser.add_argument('--data', type=str, help='Data no formato dd-mm-yyyy')
    args = parser.parse_args()

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

    # Enviando a requisicao e capturando tags TD do html
    response = requests.post(url, headers=headers, data=payload)
    print(response.status_code)
    site = BeautifulSoup(response.text, "html.parser")
    tables = site.find_all("table")
    print(len(tables))

    # Funcao para limpar espacos extras nas strings
    def remover_espacos_extras(string):
        # Divide a string em palavras
        palavras = string.split()

        # Une as palavras novamente com um único espaço entre elas
        string_limpa = ' '.join(palavras)
        return string_limpa

    # Filtrando as td para a refeicao correspondente
    #for x in range(len(td)):



if __name__ == '__main__':
    main()