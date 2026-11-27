from datetime import date, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from armazenamento import PomarSQLite
from pomar import ArvoreFruto, Colheita


class OcorrenciasTest(TestCase):
    def setUp(self):
        self.bd = PomarSQLite()
        self.bd.adicionar_arvore("M-01", "Macieira", "Bravo de Esmolfe")
        self.bd.adicionar_arvore("M-02", "Macieira", "")
        self.hoje = date.today()

    def test_recorrencia_e_independencia_por_arvore(self):
        doenca = "pedrado-macieira"
        primeiro = self.bd.observar("M-01", self.hoje, "Manchas nas folhas")
        segundo = self.bd.observar("M-01", self.hoje, "Manchas no fruto")
        vizinha = self.bd.observar("M-02", self.hoje, "Manchas nas folhas")
        self.bd.confirmar("M-01", primeiro, doenca)
        self.bd.confirmar("M-02", vizinha, doenca)
        with self.assertRaisesRegex(ValueError, "ocorrência ativa"):
            self.bd.confirmar("M-01", segundo, doenca)
        self.assertIsNone(self.bd.ocorrencias("M-01")[0]["doenca"])
        self.bd.fechar("M-01", primeiro, self.hoje, "Encerrada")
        self.bd.confirmar("M-01", segundo, doenca)
        self.assertIsNone(self.bd.ocorrencias("M-02")[0]["fechada_em"])

    def test_valida_sintomas_especie_e_datas(self):
        with self.assertRaisesRegex(ValueError, "sintoma"):
            self.bd.observar("M-01", self.hoje, " ")
        with self.assertRaisesRegex(ValueError, "data"):
            self.bd.observar("M-01", self.hoje + timedelta(days=1), "Manchas")
        caso = self.bd.observar("M-01", self.hoje, "Manchas")
        with self.assertRaisesRegex(ValueError, "espécie"):
            self.bd.confirmar("M-01", caso, "mancha-cerejeira")
        with self.assertRaisesRegex(ValueError, "data de fecho"):
            self.bd.fechar("M-01", caso, self.hoje - timedelta(days=1), "")
        self.bd.fechar("M-01", caso, self.hoje, "Sem identificação")
        with self.assertRaisesRegex(ValueError, "fechada"):
            self.bd.confirmar("M-01", caso, "pedrado-macieira")

    def test_persistencia_e_isolamento_da_demo(self):
        with TemporaryDirectory() as pasta:
            caminho = Path(pasta) / "pomar.sqlite3"
            bd = PomarSQLite(caminho)
            bd.adicionar_arvore("M-10", "Macieira", "")
            ArvoreFruto("M-10", bd).registar_intervencao(Colheita(self.hoje, 4.5))
            bd.observar("M-10", self.hoje, "Manchas")
            reaberto = PomarSQLite(caminho)
            self.assertEqual(list(reaberto.arvores()), ["M-10"])
            self.assertEqual(reaberto.consultar("M-10")[0]["kg"], 4.5)
            self.assertEqual(reaberto.ocorrencias("M-10")[0]["sintomas"], "Manchas")
            self.assertEqual(PomarSQLite().arvores(), {})
