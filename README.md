# O que é o Bandeco?
É uma aplicação de linha de comando que permite verificar o cardápio do restaurante universitário da Unicamp 
Limeira, com a opção de filtrar os resultados por data, refeição, vegetariano etc.

# Instalação

## Debian Package
> Do lado direito da página do repositório escolha um release e faça download

> $ sudo dpkg -i nome_do_arquivo.deb

> $ bandeco

## Via pip / Repositório
> $ git clone https://github.com/zedutra/bandeco-unicamp-limeira.git

> $ cd bandeco-unicamp-limeira

> $ pip install .

Ou executando diretamente o script:

> $ python3 bandeco/bandeco.py

# Uso
> $ bandeco -jap --data=18-05-2024

    Almoço Padrão:
      Acompanhamentos: ARROZ E FEIJÃO
      Prato Principal: Frango a espanhola
      Guarnição: Batata palha
      Salada: Couve
      Sobremesa: Banana
      Refresco: Uva
      Extra: PÃO E CAFÉ
      Nota Técnica: Contém glúten no pão. Não contém ovos e lactose. Contém glúten na batata palha.

    Jantar Padrão:
      Acompanhamentos: ARROZ E FEIJÃO
      Prato Principal: Moqueca de peixe
      Guarnição: Abobrinha aromatizada com alecrim
      Salada: Jiló
      Sobremesa: Maçã
      Refresco: Uva
      Extra: PÃO E CAFÉ
      Nota Técnica: Contém glúten no pão. Não contém ovos e lactose.

> $ bandeco -h

    usage: bandeco [-h] [-v] [-p] [-a] [-j] [-c] [--data DATA | -m | -o] [--json] [--sem-cor] [--sem-cache]

    Programa para verificar o cardápio do restaurante universitário da Unicamp de Limeira

    options:
      -h, --help            show this help message and exit
      -v, -vegano, --vegano
                            Filtra pelas refeições veganas
      -p, -padrao, --padrao
                            Filtra pelas refeições padrão
      -a, -almoco, --almoco
                            Requisita o cardápio do almoço
      -j, -jantar, --jantar
                            Requisita o cardápio do jantar
      -c, -cafe, --cafe     Requisita o cardápio do café da manhã
      --data DATA           Data no formato dd-mm-yyyy
      -m, --amanha          Requisita o cardápio de amanhã
      -o, --ontem           Requisita o cardápio de ontem
      --json                Exibe o cardápio em formato JSON
      --sem-cor             Desativa a formatação colorida no terminal
      --sem-cache           Ignora o cache local e força nova requisição

# Testes
> $ python3 -m unittest discover -s tests