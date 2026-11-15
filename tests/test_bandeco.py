from datetime import datetime
from pathlib import Path
import tempfile
import unittest
from bandeco.bandeco import (
    carregar_cache,
    extrair_cardapio,
    filtrar_cardapio,
    formatar_string,
    resolver_data,
    salvar_cache,
)

HTML_EXEMPLO = """
<html>
<body>
  <table>
    <tr><td>ACOMPANHAMENTOS: ARROZ E FEIJÃO</td></tr>
    <tr><td>PRATO PRINCIPAL: Frango a espanhola</td></tr>
    <tr><td>GUARNIÇÃO: Batata palha</td></tr>
    <tr><td>SALADA: Couve</td></tr>
    <tr><td>SOBREMESA: Banana</td></tr>
    <tr><td>REFRESCO: Uva</td></tr>
    <tr><td>EXTRA: PÃO E CAFÉ</td></tr>
    <tr><td>NOTA TÉCNICA: Atenção: Contém glúten: pão e batata palha.</td></tr>
  </table>
  <table>
    <tr><td>ACOMPANHAMENTOS: ARROZ INTEGRAL E FEIJÃO</td></tr>
    <tr><td>PRATO PRINCIPAL: Grão-de-bico ao curry</td></tr>
    <tr><td>GUARNIÇÃO: Batata palha</td></tr>
    <tr><td>SALADA: Couve</td></tr>
    <tr><td>SOBREMESA: Banana</td></tr>
    <tr><td>REFRESCO: Uva</td></tr>
    <tr><td>EXTRA: PÃO E CAFÉ</td></tr>
    <tr><td>NOTA TÉCNICA: Contém glúten no pão.</td></tr>
  </table>
  <table>
    <tr><td>ACOMPANHAMENTOS: ARROZ E FEIJÃO</td></tr>
    <tr><td>PRATO PRINCIPAL: Moqueca de peixe</td></tr>
    <tr><td>GUARNIÇÃO: Abobrinha aromatizada com alecrim</td></tr>
    <tr><td>SALADA: Jiló</td></tr>
    <tr><td>SOBREMESA: Maçã</td></tr>
    <tr><td>REFRESCO: Uva</td></tr>
    <tr><td>EXTRA: PÃO E CAFÉ</td></tr>
    <tr><td>NOTA TÉCNICA: Contém glúten no pão.</td></tr>
  </table>
  <table>
    <tr><td>ACOMPANHAMENTOS: ARROZ INTEGRAL E FEIJÃO</td></tr>
    <tr><td>PRATO PRINCIPAL: Moqueca de banana-da-terra</td></tr>
    <tr><td>GUARNIÇÃO: Abobrinha aromatizada com alecrim</td></tr>
    <tr><td>SALADA: Jiló</td></tr>
    <tr><td>SOBREMESA: Maçã</td></tr>
    <tr><td>REFRESCO: Uva</td></tr>
    <tr><td>EXTRA: PÃO E CAFÉ</td></tr>
    <tr><td>NOTA TÉCNICA: Contém glúten no pão.</td></tr>
  </table>
  <table>
    <tr><td>COMIDA: Pão francês com margarina e fruta</td></tr>
    <tr><td>BEBIDA: Café e leite</td></tr>
  </table>
</body>
</html>
"""


class TestBandeco(unittest.TestCase):
    def test_formatar_string_preserva_dois_pontos_extras(self):
        texto = "  NOTA TÉCNICA:   Atenção: Contém glúten: trigo  "
        self.assertEqual(formatar_string(texto), "Atenção: Contém glúten: trigo")

    def test_formatar_string_sem_dois_pontos(self):
        self.assertEqual(formatar_string("  ARROZ   E   FEIJÃO "), "ARROZ E FEIJÃO")

    def test_resolver_data_atalhos_e_formato(self):
        ref = datetime(2024, 5, 18)
        self.assertEqual(resolver_data(referencia=ref), "2024-05-18")
        self.assertEqual(resolver_data(amanha=True, referencia=ref), "2024-05-19")
        self.assertEqual(resolver_data(ontem=True, referencia=ref), "2024-05-17")
        self.assertEqual(resolver_data("25-12-2024", referencia=ref), "2024-12-25")

    def test_resolver_data_invalida(self):
        with self.assertRaises(ValueError):
            resolver_data("2024-05-18")

    def test_extrair_cardapio_completo(self):
        cardapio = extrair_cardapio(HTML_EXEMPLO)
        self.assertEqual(len(cardapio), 5)
        self.assertEqual(cardapio["Almoço Padrão"]["Prato Principal"], "Frango a espanhola")
        self.assertEqual(
            cardapio["Almoço Padrão"]["Nota Técnica"],
            "Atenção: Contém glúten: pão e batata palha.",
        )
        self.assertEqual(cardapio["Café da Manhã"]["Bebida"], "Café e leite")

    def test_extrair_cardapio_sem_tabelas(self):
        self.assertEqual(extrair_cardapio("<html><body>Sem cardápio</body></html>"), {})

    def test_extrair_cardapio_refeicao_nao_cadastrada(self):
        html_domingo = HTML_EXEMPLO.replace(
            """  <table>
    <tr><td>ACOMPANHAMENTOS: ARROZ E FEIJÃO</td></tr>
    <tr><td>PRATO PRINCIPAL: Moqueca de peixe</td></tr>
    <tr><td>GUARNIÇÃO: Abobrinha aromatizada com alecrim</td></tr>
    <tr><td>SALADA: Jiló</td></tr>
    <tr><td>SOBREMESA: Maçã</td></tr>
    <tr><td>REFRESCO: Uva</td></tr>
    <tr><td>EXTRA: PÃO E CAFÉ</td></tr>
    <tr><td>NOTA TÉCNICA: Contém glúten no pão.</td></tr>
  </table>""",
            "<table><tr><td>NÃO HÁ CARDÁPIO CADASTRADO!</td></tr></table>",
        )
        cardapio = extrair_cardapio(html_domingo)
        self.assertEqual(
            cardapio["Jantar Padrão"],
            {"Aviso": "NÃO HÁ CARDÁPIO CADASTRADO!"},
        )

    def test_filtrar_cardapio_opcoes(self):
        completo = extrair_cardapio(HTML_EXEMPLO)

        apenas_almoco_padrao = filtrar_cardapio(completo, almoco=True, padrao=True)
        self.assertEqual(list(apenas_almoco_padrao.keys()), ["Almoço Padrão"])

        apenas_jantar_vegano = filtrar_cardapio(completo, jantar=True, vegano=True)
        self.assertEqual(list(apenas_jantar_vegano.keys()), ["Jantar Vegano"])

        # Se passar ambos vegano e padrao, deve manter ambos
        ambos_almoco = filtrar_cardapio(completo, almoco=True, vegano=True, padrao=True)
        self.assertEqual(list(ambos_almoco.keys()), ["Almoço Padrão", "Almoço Vegano"])

    def test_cache_local(self):
        completo = extrair_cardapio(HTML_EXEMPLO)
        with tempfile.TemporaryDirectory() as tmp_dir:
            pasta = Path(tmp_dir)
            salvar_cache("2024-05-18", completo, diretorio_cache=pasta)
            carregado = carregar_cache("2024-05-18", diretorio_cache=pasta)
            self.assertEqual(carregado, completo)


if __name__ == "__main__":
    unittest.main()
