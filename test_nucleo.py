import unittest
from datetime import date
from pomar import *
D = date(2026, 11, 11)
class TestPomar(unittest.TestCase):
    def test_abc_sem_descricao_impede_criacao(self):
        # Valida prevenção do cenário C1 identificado na AF5.1.
        class Incompleta(Intervencao):
            pass
        with self.assertRaises(TypeError):
            Incompleta(D)
    def test_descricao_preserva_estado_e_aceita_peso_opcional(self):
        # Valida prevenção do cenário C2 identificado na AF5.1.
        for acao in (Poda(D), Colheita(D), Colheita(D, 0), Colheita(D, 5)):
            with self.subTest(dados=vars(acao)):
                antes = vars(acao).copy()
                texto = acao.descricao()
                self.assertIsInstance(texto, str, "Descrição deve ser texto")
                self.assertTrue(texto.strip(), "Descrição deve ter conteúdo")
                self.assertEqual(texto, acao.descricao(), "Texto deve ser estável")
                self.assertEqual(antes, vars(acao), "Consulta não altera dados")
    def test_colheita_negativa_rejeitada(self):
        with self.assertRaisesRegex(ValueError, "quantidade não pode ser negativa"):
            Colheita(D, -5)
    def test_adaptador_independente_descreve(self):
        acao = AdaptadorImportacao(D, "Tratamento", "Migrado")
        self.assertNotIsInstance(acao, Intervencao)
        self.assertEqual(acao.descricao(), "Migrado", "Texto deve ser preservado")
    def test_registo_polimorfico_e_consulta_filtrada(self):
        # Valida prevenção do cenário C1 identificado na AF5.1.
        class Rega(Intervencao):
            tipo = "Rega"
            def descricao(self):
                return "Rega de 10 litros."
        mem = Memoria()
        arvore = ArvoreFruto("M-01", mem)
        acoes = [Poda(D), Colheita(D, 5), Rega(D),
                 AdaptadorImportacao(D, "Tratamento", "  Migrado  ")]
        for acao in acoes:
            arvore.registar_intervencao(acao)
        registar("M-02", Poda(D), mem)
        self.assertEqual(len(arvore.historico()), 4, "Só registos da M-01")
        self.assertEqual(len(mem.registos), 5, "Uma gravação por chamada")
        self.assertEqual(arvore.historico("Colheita")[0],
                         dict(arvore="M-01", data=D, tipo="Colheita",
                              descricao=acoes[1].descricao(), kg=5))
        self.assertEqual(arvore.historico()[-1]["descricao"], "Migrado")
    def test_descricao_invalida_nao_altera_historico(self):
        # Valida prevenção do cenário C2 identificado na AF5.1.
        for texto, erro in [("   ", ValueError), (7, TypeError)]:
            with self.subTest(texto=texto):
                mem = Memoria()
                acao = AdaptadorImportacao(D, "Poda", texto)
                with self.assertRaises(erro):
                    registar("M-01", acao, mem)
                self.assertEqual(mem.registos, [], "Histórico deve ficar intacto")
        adaptador = AdaptadorImportacao(D, "Colheita", "Colheita importada")
        adaptador.kg = -5
        mem = Memoria()
        with self.assertRaisesRegex(ValueError, "quantidade não pode ser negativa"):
            registar("M-01", adaptador, mem)
        self.assertEqual(mem.registos, [], "Peso inválido não pode ser gravado")
    def test_falha_de_escrita_nao_confirma_sucesso(self):
        # Valida prevenção do cenário C3 identificado na AF5.1.
        class Falha(Memoria):
            def guardar(self, registo):
                raise OSError("Não foi possível guardar.")
        mem = Falha()
        with self.assertRaisesRegex(OSError, "Não foi possível guardar"):
            ArvoreFruto("M-01", mem).registar_intervencao(Poda(D))
        self.assertEqual(mem.registos, [], "Sem entrada se a escrita falhar")
