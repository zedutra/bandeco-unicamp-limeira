import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# Valores constantes
URL = "https://www.sar.unicamp.br/RU/view/site/cardapio.php"
REFEICAO_KEYS = ('Acompanhamentos', 'Prato Principal', 'Guarnição', 'Salada', 'Sobremesa', 'Refresco', 'Extra', 'Nota Técnica')
CAFE_KEYS = ('Comida', 'Bebida')
DATA_INICIAL = datetime.strptime("2014-01-01", "%Y-%m-%d")
DATA_FINAL = datetime.strptime("2024-12-31", "%Y-%m-%d")

# Funcao para limpar espacos extras nas strings
def formatarString(string):
    palavras = string.split()
    stringLimpa = ' '.join(palavras)
    try:
        stringDividida = stringLimpa.split(':')
        stringFormatada = stringDividida[1].strip()
        return stringFormatada
    except:
        return stringLimpa

def getSite(data):
    payload = {
        'data': data
    }
    headers = {
        "Host": "www.sar.unicamp.br",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    }
    try:
        response = requests.post(URL, headers=headers, data=payload)
        if response.status_code != 200:
            print('Não foi possível obter informações do cardápio')
            print(f'Error: {response.status_code}')
            exit()
    except Exception as e:
        print('Não foi possível obter informações do cardápio')
        exit()

    site = BeautifulSoup(response.text, "html.parser")
    return site

def getCardapio(site):
    # Procurando as tabelas de cada refeicao
    tables = site.find_all("table")

    # Definindo dicionarios
    almocoPadrao = dict.fromkeys(REFEICAO_KEYS)
    almocoVegano = dict.fromkeys(REFEICAO_KEYS)
    jantarPadrao = dict.fromkeys(REFEICAO_KEYS)
    jantarVegano = dict.fromkeys(REFEICAO_KEYS)
    cafeManha = dict.fromkeys(CAFE_KEYS)
    refeicoes = (almocoPadrao, almocoVegano, jantarPadrao, jantarVegano, cafeManha)

    # Formatando informacoes no html para dicionarios
    for x in range(len(refeicoes)):
        td_comidas = tables[x].find_all('td')
        for td in range(len(td_comidas)):
            comida = formatarString(td_comidas[td].getText())
            if refeicoes[x] != cafeManha:
                refeicoes[x].update({REFEICAO_KEYS[td]: comida})
            else:
                refeicoes[x].update({CAFE_KEYS[td]: comida})

    # Montando o cardapio a ser exibido
    cardapio = {
        'Almoço Padrão': almocoPadrao,
        'Almoço Vegano': almocoVegano,
        'Jantar Padrão': jantarPadrao,
        'Jantar Vegano': jantarVegano,
        # 'Café da Manhã': cafeManha
    }

    return cardapio

def main():
    # Dados das refeicoes
    almocoPadraoDados = []
    almocoVeganoDados = []
    jantarPadraoDados = []
    jantarVeganoDados = []
    # cafeDados = []    

    # Percorrer os dias entre as duas datas
    dataAtual = DATA_INICIAL

    while dataAtual <= DATA_FINAL:
        dataStr = dataAtual.strftime('%Y-%m-%d')
        site = getSite(dataStr)
        cardapio = getCardapio(site)

        if cardapio['Almoço Padrão'].get('Prato Principal'):
            almocoPadraoDados.append({
                'Data': dataStr,
                **cardapio['Almoço Padrão']
            })

        if cardapio['Almoço Vegano'].get('Prato Principal'):
            almocoVeganoDados.append({
                'Data': dataStr,
                **cardapio['Almoço Vegano']
            })

        if cardapio['Jantar Padrão'].get('Prato Principal'):
            jantarPadraoDados.append({
                'Data': dataStr,
                **cardapio['Jantar Padrão']
            })

        if cardapio['Jantar Vegano'].get('Prato Principal'):
            jantarVeganoDados.append({
                'Data': dataStr,
                **cardapio['Jantar Vegano']
            })

        # if cardapio['Café da Manhã'].get('Comida'):
        #     cafeDados.append({
        #         'Data': dataStr,
        #         **cardapio['Café da Manhã']
        #     })

        dataAtual += timedelta(days=1)  # Avança um dia

    dfAlmocoPadrao = pd.DataFrame(almocoPadraoDados)
    dfAlmocoVegano = pd.DataFrame(almocoVeganoDados)
    dfJantarPadrao = pd.DataFrame(jantarPadraoDados)
    dfJantarVegano = pd.DataFrame(jantarVeganoDados)
    # dfCafe = pd.DataFrame(cafeDados)
    
    dfAlmocoPadrao.to_csv('almoco_padrao.csv', index=False)
    dfAlmocoVegano.to_csv('almoco_vegano.csv', index=False)
    dfJantarPadrao.to_csv('jantar_padrao.csv', index=False)
    dfJantarVegano.to_csv('jantar_vegano.csv', index=False)
    # dfCafe.to_csv('cafe_da_manha.csv', index=False)

if __name__ == '__main__':
    main()