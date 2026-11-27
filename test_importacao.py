import unittest
from datetime import date
from pomar import Memoria, Importacao

D = date(2026, 11, 11)
def linha(tipo="Colheita", kg=5):
    return dict(arvore="M-01", data=D, tipo=tipo, kg=kg, descricao="Importada")

class TestImportacao(unittest.TestCase):
    def test_lote_pausa_so_em_erro_e_conserva_pendente(self):
        mem = Memoria()
        imp = Importacao(mem)
        pedidos = []
        def decidir(dados, aviso):
            pedidos.append((dados, aviso))
            return "manter", {}, False
        saida = imp.importar([linha(), linha(kg=-5), linha("Poda")], decidir)
        self.assertEqual(len(pedidos), 1)
        self.assertIn("negativa", pedidos[0][1])
        self.assertEqual(saida[1], "Pendente")
        self.assertEqual(len(mem.consultar("M-01")), 2)
        self.assertEqual(imp.pendentes[0]["dados"]["kg"], -5)

    def test_correcao_depende_de_confirmacao(self):
        for confirmar in (False, True):
            with self.subTest(confirmar=confirmar):
                mem = Memoria()
                imp = Importacao(mem)
                imp.importar([linha(kg=-5)],
                             lambda dados, aviso: ("corrigir", {"kg": 5}, confirmar))
                self.assertEqual(len(mem.registos), int(confirmar))
                self.assertEqual(len(imp.pendentes), int(not confirmar))
                if not confirmar:
                    self.assertEqual(imp.pendentes[0]["original"]["kg"], -5)
                    self.assertEqual(imp.pendentes[0]["dados"]["kg"], 5)
                else:
                    self.assertIn("5 kg", mem.registos[0]["descricao"])

    def test_tipo_ausente_pode_corrigir_eliminar_ou_adiar(self):
        for escolha in ("corrigir", "eliminar", "manter"):
            with self.subTest(escolha=escolha):
                mem = Memoria()
                imp = Importacao(mem)
                imp.importar([linha(tipo="")],
                             lambda dados, aviso: (escolha, {"tipo": "Poda"}, True))
                self.assertEqual(len(mem.registos), int(escolha == "corrigir"))
                self.assertEqual(len(imp.pendentes), int(escolha == "manter"))

    def test_falha_de_gravacao_nao_pede_correcao_de_dados(self):
        class Falha(Memoria):
            def guardar(self, registo):
                raise OSError("Falha de gravação")
        imp = Importacao(Falha())
        def decidir(dados, aviso):
            self.fail("Falha de armazenamento não é erro de dados.")
        with self.assertRaises(OSError):
            imp.importar([linha()], decidir)
        self.assertEqual(imp.armazenamento.registos, [])

class TestTiposPermitidos(unittest.TestCase):
    def test_tipo_nao_permitido_fica_pendente(self):
        mem = Memoria()
        imp = Importacao(mem)
        avisos = []
        def decidir(dados, aviso):
            avisos.append(aviso)
            return "manter", {}, False
        imp.importar([linha(tipo="LavarCarro")], decidir)
        self.assertEqual(mem.registos, [])
        self.assertEqual(len(imp.pendentes), 1)
        self.assertIn("não permitido", avisos[0])

class TestRegressoes(unittest.TestCase):
    def test_codigo_com_espacos_grava_e_consulta_mesma_arvore(self):
        from pomar import ArvoreFruto, Poda, registar
        mem = Memoria()
        arvore = ArvoreFruto(" M-01 ", mem)
        arvore.registar_intervencao(Poda(D))
        registar(" M-01 ", Poda(D), mem)
        self.assertEqual(arvore.codigo, "M-01")
        self.assertEqual(len(arvore.historico()), 2)
        self.assertEqual(mem.consultar(" M-01 "), mem.consultar("M-01"))
        self.assertTrue(all(r["arvore"] == "M-01" for r in mem.registos))
        self.assertEqual(mem.consultar("M-02"), [])

    def test_pesos_invalidos_rejeitados_na_origem_e_no_adaptador(self):
        from pomar import Colheita, AdaptadorImportacao, registar
        for kg in [float("nan"), float("inf"), -float("inf"), "5", True]:
            with self.subTest(kg=kg):
                with self.assertRaises(ValueError):
                    Colheita(D, kg)
                mem = Memoria()
                acao = AdaptadorImportacao(D, "Colheita", "Importada")
                acao.kg = kg
                with self.assertRaises(ValueError):
                    registar("M-01", acao, mem)
                self.assertEqual(mem.registos, [])
                imp = Importacao(mem)
                imp.importar([linha(kg=kg)],
                             lambda dados, aviso: ("manter", {}, False))
                self.assertEqual(len(imp.pendentes), 1)
                self.assertEqual(mem.registos, [])

    def test_importacao_valida_peso_antes_de_escolher_classe(self):
        for tipo in ("Poda", "Tratamento", "Rega"):
            for kg in (-5, float("nan"), float("inf"), "5", True):
                with self.subTest(tipo=tipo, kg=kg):
                    mem = Memoria()
                    imp = Importacao(mem)
                    avisos = []
                    def decidir(dados, aviso):
                        avisos.append(aviso)
                        return "manter", {}, False
                    saida = imp.importar([linha(tipo, kg)], decidir)
                    self.assertEqual(saida, ["Pendente"])
                    self.assertEqual(len(avisos), 1)
                    self.assertIn("quantidade", avisos[0])
                    self.assertEqual(mem.consultar("M-01"), [])
                    self.assertEqual(len(imp.pendentes), 1)
                    self.assertEqual(imp.pendentes[0]["original"]["tipo"], tipo)
                    self.assertIs(imp.pendentes[0]["original"]["kg"], kg)
