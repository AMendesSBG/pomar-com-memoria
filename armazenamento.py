"""Persistência SQLite para árvores, intervenções e ocorrências."""

import sqlite3
from contextlib import contextmanager
from datetime import date
from pathlib import Path

from doencas import DOENCAS
from pomar import normalizar_codigo


class PomarSQLite:
    def __init__(self, caminho=None):
        self.caminho = Path(caminho) if caminho else None
        if self.caminho:
            self.caminho.parent.mkdir(parents=True, exist_ok=True)
        self._demo = sqlite3.connect(":memory:", check_same_thread=False) if not caminho else None
        with self._ligacao() as bd:
            bd.executescript("""
                CREATE TABLE IF NOT EXISTS arvores (
                    codigo TEXT PRIMARY KEY, especie TEXT NOT NULL, variedade TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS intervencoes (
                    id INTEGER PRIMARY KEY, arvore TEXT NOT NULL REFERENCES arvores(codigo),
                    data TEXT NOT NULL, tipo TEXT NOT NULL, descricao TEXT NOT NULL, kg REAL
                );
                CREATE TABLE IF NOT EXISTS ocorrencias (
                    id INTEGER PRIMARY KEY, arvore TEXT NOT NULL REFERENCES arvores(codigo),
                    observada_em TEXT NOT NULL, sintomas TEXT NOT NULL, doenca TEXT,
                    fechada_em TEXT, nota_fecho TEXT,
                    CHECK (fechada_em IS NULL OR fechada_em >= observada_em)
                );
                CREATE UNIQUE INDEX IF NOT EXISTS ocorrencia_ativa_por_doenca
                    ON ocorrencias(arvore, doenca)
                    WHERE fechada_em IS NULL AND doenca IS NOT NULL;
            """)

    @contextmanager
    def _ligacao(self):
        bd = self._demo if self._demo is not None else sqlite3.connect(self.caminho)
        bd.row_factory = sqlite3.Row
        bd.execute("PRAGMA foreign_keys = ON")
        try:
            with bd:
                yield bd
        finally:
            if self._demo is None:
                bd.close()

    def adicionar_arvore(self, codigo, especie, variedade):
        codigo = normalizar_codigo(codigo)
        especie, variedade = especie.strip(), variedade.strip()
        if not especie:
            raise ValueError("Indica a espécie.")
        with self._ligacao() as bd:
            resultado = bd.execute(
                "INSERT INTO arvores VALUES (?, ?, ?) ON CONFLICT(codigo) DO NOTHING",
                (codigo, especie, variedade),
            )
            if resultado.rowcount == 0:
                raise ValueError("Já existe uma árvore com esse código.")

    def arvores(self):
        with self._ligacao() as bd:
            return {r["codigo"]: (r["especie"], r["variedade"]) for r in bd.execute(
                "SELECT * FROM arvores ORDER BY codigo"
            )}

    def guardar(self, registo):
        with self._ligacao() as bd:
            bd.execute("""
                INSERT INTO intervencoes (arvore, data, tipo, descricao, kg)
                VALUES (:arvore, :data, :tipo, :descricao, :kg)
            """, {**registo, "data": registo["data"].isoformat()})

    def consultar(self, arvore, tipo=None):
        with self._ligacao() as bd:
            linhas = bd.execute("""
                SELECT arvore, data, tipo, descricao, kg FROM intervencoes
                WHERE arvore = ? AND (? IS NULL OR tipo = ?) ORDER BY id
            """, (normalizar_codigo(arvore), tipo, tipo))
            return [{**r, "data": date.fromisoformat(r["data"])} for r in linhas]

    def ocorrencias(self, arvore):
        with self._ligacao() as bd:
            return [dict(r) for r in bd.execute("""
                SELECT * FROM ocorrencias WHERE arvore = ?
                ORDER BY observada_em DESC, id DESC
            """, (normalizar_codigo(arvore),))]

    @staticmethod
    def _validar_doenca(doenca, especie):
        ficha = DOENCAS.get(doenca)
        if ficha is None or especie.casefold() not in {s.casefold() for s in ficha.especies}:
            raise ValueError("Escolhe uma ficha disponível para esta espécie.")

    def observar(self, arvore, data, sintomas):
        arvore = normalizar_codigo(arvore)
        if not sintomas.strip():
            raise ValueError("Descreve pelo menos um sintoma observado.")
        if type(data) is not date or data > date.today():
            raise ValueError("Indica uma data de observação válida.")
        with self._ligacao() as bd:
            if not bd.execute("SELECT 1 FROM arvores WHERE codigo = ?", (arvore,)).fetchone():
                raise ValueError("A árvore indicada não existe.")
            resultado = bd.execute("""
                INSERT INTO ocorrencias (arvore, observada_em, sintomas) VALUES (?, ?, ?)
            """, (arvore, data.isoformat(), sintomas.strip()))
            return resultado.lastrowid

    def confirmar(self, arvore, ocorrencia, doenca):
        with self._ligacao() as bd:
            linha = bd.execute("SELECT especie FROM arvores WHERE codigo = ?", (arvore,)).fetchone()
            if linha is None:
                raise ValueError("A árvore indicada não existe.")
            self._validar_doenca(doenca, linha["especie"])
            try:
                resultado = bd.execute("""
                    UPDATE ocorrencias SET doenca = ?
                    WHERE id = ? AND arvore = ? AND fechada_em IS NULL AND doenca IS NULL
                """, (doenca, ocorrencia, arvore))
            except sqlite3.IntegrityError as erro:
                raise ValueError("Já existe uma ocorrência ativa desta doença nesta árvore.") from erro
            if resultado.rowcount == 0:
                raise ValueError("A ocorrência já foi confirmada, foi fechada ou não existe.")

    def fechar(self, arvore, ocorrencia, data, nota):
        if type(data) is not date or data > date.today():
            raise ValueError("Indica uma data de fecho válida.")
        with self._ligacao() as bd:
            resultado = bd.execute("""
                UPDATE ocorrencias SET fechada_em = ?, nota_fecho = ?
                WHERE id = ? AND arvore = ? AND fechada_em IS NULL AND observada_em <= ?
            """, (data.isoformat(), nota.strip(), ocorrencia, arvore, data.isoformat()))
            if resultado.rowcount == 0:
                raise ValueError("Verifica se a ocorrência continua aberta e se a data de fecho é igual ou posterior à observação.")
