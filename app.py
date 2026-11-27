from datetime import date, timedelta
from os import environ

import streamlit as st

from armazenamento import PomarSQLite
from pomar import ArvoreFruto, Colheita, Poda, validar_peso
from saude_ui import apresentar_saude, biblioteca

ARVORES_DEMO = {
    "M-01": ("Macieira", "Bravo de Esmolfe"),
    "P-01": ("Pereira", "Rocha"),
    "C-01": ("Cerejeira", "Burlat"),
}
FILTROS = {"Todas": None, "Podas": "Poda", "Colheitas": "Colheita"}


def inicializar():
    memoria = PomarSQLite(environ.get("POMAR_DB_PATH"))
    if memoria.caminho is None:
        for codigo, (especie, variedade) in ARVORES_DEMO.items():
            memoria.adicionar_arvore(codigo, especie, variedade)
        hoje = date.today()
        ArvoreFruto("M-01", memoria).registar_intervencao(Poda(hoje - timedelta(days=18)))
        ArvoreFruto("M-01", memoria).registar_intervencao(
            Colheita(hoje - timedelta(days=7), 8)
        )
        ArvoreFruto("P-01", memoria).registar_intervencao(Poda(hoje - timedelta(days=12)))
        caso = memoria.observar("M-01", hoje - timedelta(days=5), "Manchas verde-azeitona nas folhas.")
        memoria.confirmar("M-01", caso, "pedrado-macieira")
    st.session_state.memoria = memoria
    st.session_state.arvore = None
    st.session_state.formulario_aberto = False


def selecionar_arvore(codigo):
    st.session_state.arvore = codigo
    st.session_state.formulario_aberto = False
    st.session_state.pop("aviso_colheita", None)
    st.session_state.pop("filtro_historico", None)


def apresentar_arvores(bd, arvores):
    st.subheader("Árvores")
    if st.session_state.pop("arvore_guardada", False):
        st.success("Árvore adicionada.")
    with st.expander("Adicionar árvore", expanded=not arvores):
        with st.form("nova_arvore"):
            codigo = st.text_input("Código", placeholder="Ex.: M-04")
            especie = st.text_input("Espécie", placeholder="Ex.: Macieira")
            variedade = st.text_input("Variedade", placeholder="Opcional")
            if st.form_submit_button("Guardar árvore"):
                try:
                    bd.adicionar_arvore(codigo, especie, variedade)
                except ValueError as erro:
                    st.error(str(erro))
                else:
                    st.session_state.arvore_guardada = True
                    st.rerun()
    for codigo, (especie, variedade) in arvores.items():
        with st.container(border=True):
            st.text(" · ".join(filter(None, (especie, variedade))))
            st.caption(codigo)
            st.button(
                "Ver histórico",
                key=f"abrir_{codigo}",
                on_click=selecionar_arvore,
                args=(codigo,),
            )


def registar_colheita(arvore):
    st.markdown("#### Registar colheita")
    with st.form("nova_colheita"):
        data_colheita = st.date_input("Data", value=date.today(), format="DD/MM/YYYY")
        peso_texto = st.text_input(
            "Peso (kg)", placeholder="Opcional", help="Aceita vírgula ou ponto decimal."
        )
        aviso_peso = st.empty()
        guardar = st.form_submit_button("Guardar colheita", type="primary")

    if st.button("Cancelar"):
        st.session_state.formulario_aberto = False
        st.rerun()

    if guardar:
        try:
            peso = float(peso_texto.strip().replace(",", ".")) if peso_texto.strip() else None
        except ValueError:
            aviso_peso.error("Introduz um peso numérico, como 5 ou 2,5 kg.")
            return

        try:
            validar_peso(peso)
        except ValueError:
            aviso_peso.error("O peso deve ser um número finito igual ou superior a 0 kg.")
            return

        arvore.registar_intervencao(Colheita(data_colheita, peso))
        st.session_state.aviso_colheita = "Colheita guardada no histórico."
        st.session_state.filtro_historico = "Todas"
        st.session_state.formulario_aberto = False
        st.rerun()


def apresentar_ficha(codigo, bd, arvores):
    if st.button("← Voltar às árvores", on_click=selecionar_arvore, args=(None,)):
        return

    especie, variedade = arvores[codigo]
    st.subheader(" · ".join(filter(None, (especie, variedade))))
    st.caption(codigo)
    seccao = st.radio("Ficha da árvore", ["Histórico", "Saúde"], horizontal=True)
    if seccao == "Saúde":
        apresentar_saude(bd, codigo, especie)
        return

    arvore = ArvoreFruto(codigo, bd)

    aviso = st.session_state.pop("aviso_colheita", None)
    if aviso:
        st.success(aviso)

    if st.session_state.formulario_aberto:
        registar_colheita(arvore)
    elif st.button("Registar colheita", type="primary"):
        st.session_state.formulario_aberto = True
        st.rerun()

    st.markdown("#### Histórico")
    filtro = st.radio("Filtrar histórico", FILTROS, horizontal=True, key="filtro_historico")
    registos = sorted(
        reversed(arvore.historico(FILTROS[filtro])),
        key=lambda registo: registo["data"],
        reverse=True,
    )
    if not registos:
        st.info("Ainda não existem registos para este filtro.")

    for registo in registos:
        with st.container(border=True):
            st.markdown(f"**{registo['tipo']}** · {registo['data']:%d/%m/%Y}")
            st.write(registo["descricao"])


st.set_page_config(page_title="Pomar com Memória", page_icon="🌳", layout="centered")
if "memoria" not in st.session_state:
    inicializar()

st.title("Pomar com Memória")
bd = st.session_state.memoria
if bd.caminho is None:
    st.caption("Demonstração com árvores fictícias. Os registos duram durante a sessão.")
else:
    st.caption("Pomar com registos persistentes.")

pagina = st.sidebar.radio("Navegação", ["Pomar", "Biblioteca de doenças"])
if pagina == "Biblioteca de doenças":
    st.subheader("Biblioteca de doenças")
    biblioteca()
else:
    codigo = st.session_state.arvore
    arvores = bd.arvores()
    if codigo in arvores:
        apresentar_ficha(codigo, bd, arvores)
    else:
        apresentar_arvores(bd, arvores)
