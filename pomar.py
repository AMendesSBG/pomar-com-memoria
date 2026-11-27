from abc import ABC, abstractmethod
from datetime import date
from math import isfinite

TIPOS_PERMITIDOS = {"Poda", "Tratamento", "Colheita", "Rega"}

def validar_peso(kg):
    if kg is None:
        return
    if type(kg) not in (int, float) or (type(kg) is float and not isfinite(kg)):
        raise ValueError("A quantidade deve ser numérica e finita.")
    if kg < 0:
        raise ValueError("Erro de quantidade: a quantidade não pode ser negativa.")

def normalizar_codigo(codigo):
    if not isinstance(codigo, str) or not codigo.strip():
        raise ValueError("Identificador de árvore inválido.")
    return codigo.strip()

class Intervencao(ABC):
    # ABC identificada na 5.3.1 para o contrato de descrição.
    def __init__(self, data):
        self.data = data

    @abstractmethod
    def descricao(self) -> str:
        """Texto com conteúdo, sem alterar dados; aceita opcionais ausentes."""
        pass

class Poda(Intervencao):
    tipo = "Poda"

    def descricao(self) -> str:
        return f"Poda realizada em {self.data:%d/%m/%Y}."

class Colheita(Intervencao):
    tipo = "Colheita"

    def __init__(self, data, kg=None):
        super().__init__(data)
        validar_peso(kg)
        self.kg = kg

    def descricao(self) -> str:
        texto = f"Colheita realizada em {self.data:%d/%m/%Y}"
        if self.kg is not None and self.kg > 0:
            texto += f", a colheita foi de {self.kg:g} kg"
        return texto + "."

class AdaptadorImportacao:
    # Protocolo informal definido na 5.3.1: descricao().
    def __init__(self, data, tipo, texto):
        self.data, self.tipo, self.texto = data, tipo, texto

    def descricao(self):
        return self.texto

class Memoria:
    def __init__(self):
        self.registos = []

    def guardar(self, registo):
        self.registos.append(dict(registo))

    def consultar(self, arvore, tipo=None):
        arvore = normalizar_codigo(arvore)
        return [dict(r) for r in self.registos
                if r["arvore"] == arvore and (tipo is None or r["tipo"] == tipo)]

def registar(arvore, acao, armazenamento):
    texto = acao.descricao()
    if not isinstance(texto, str):
        raise TypeError("A descrição tem de ser texto.")
    if not texto.strip():
        raise ValueError("A descrição não pode estar vazia nem conter apenas espaços.")
    if not isinstance(acao.tipo, str) or not acao.tipo.strip():
        raise ValueError("Indique o tipo de intervenção.")
    if acao.tipo.strip() not in TIPOS_PERMITIDOS:
        raise ValueError("Tipo de intervenção não permitido.")
    if not isinstance(acao.data, date):
        raise ValueError("Data de intervenção inválida.")
    arvore = normalizar_codigo(arvore)
    kg = getattr(acao, "kg", None)
    validar_peso(kg)
    armazenamento.guardar(dict(arvore=arvore.strip(), data=acao.data,
                               tipo=acao.tipo.strip(), descricao=texto.strip(),
                               kg=kg))
    return texto.strip()

class Importacao:
    """Só linhas com erro pedem decisão; pendentes ficam fora do histórico."""
    def __init__(self, armazenamento):
        self.armazenamento = armazenamento
        self.pendentes = []

    def importar(self, linhas, decidir):
        resultados = []
        for original in linhas:
            linha = dict(original)
            try:
                resultados.append(self._registar_linha(linha))
            except (ValueError, TypeError, KeyError, AttributeError) as erro:
                escolha, correcao, confirmado = decidir(dict(linha), str(erro))
                if escolha == "eliminar":
                    resultados.append("Eliminada")
                    continue
                if escolha == "corrigir" and confirmado:
                    linha.update(correcao)
                    try:
                        resultados.append(self._registar_linha(linha))
                        continue
                    except (ValueError, TypeError, KeyError, AttributeError) as novo:
                        erro = novo
                elif escolha == "corrigir":
                    linha.update(correcao)
                self.pendentes.append(dict(dados=linha, original=dict(original),
                                            aviso=str(erro), confirmado=False))
                resultados.append("Pendente")
        return resultados

    def _registar_linha(self, linha):
        validar_peso(linha.get("kg"))
        if linha["tipo"] == "Colheita":
            acao = Colheita(linha["data"], linha.get("kg"))
        else:
            acao = AdaptadorImportacao(linha["data"], linha["tipo"],
                                      linha["descricao"])
        return registar(linha["arvore"], acao, self.armazenamento)

class ArvoreFruto:
    """Fachada que conserva a operação planeada no UML da 5.3.1."""
    def __init__(self, codigo, armazenamento):
        self.codigo, self.armazenamento = normalizar_codigo(codigo), armazenamento

    def registar_intervencao(self, acao):
        return registar(self.codigo, acao, self.armazenamento)

    def historico(self, tipo=None):
        return self.armazenamento.consultar(self.codigo, tipo)
