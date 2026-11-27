"""Interface de observação, confirmação, fecho e consulta de fichas."""

from datetime import date

import streamlit as st

from doencas import DOENCAS


def formatar_data(valor):
    return date.fromisoformat(valor).strftime("%d/%m/%Y")


def biblioteca():
    especies = sorted({s for ficha in DOENCAS.values() for s in ficha.especies})
    especie = st.selectbox("Filtrar fichas por espécie", ["Todas", *especies])
    for ficha in DOENCAS.values():
        if especie == "Todas" or especie in ficha.especies:
            with st.container(border=True):
                st.markdown(f"#### {ficha.nome}")
                st.caption(" · ".join(ficha.especies))
                st.image(ficha.foto, caption=f"{ficha.nome} · University of Minnesota Extension", width="content")
                st.write(ficha.sintomas)
                st.write(ficha.comparar)
                st.link_button("Ver fotografias e ficha técnica", ficha.fonte)


def guardar_acao(acao, mensagem, *args):
    try:
        acao(*args)
    except ValueError as erro:
        st.error(str(erro))
    else:
        st.session_state.aviso_saude = mensagem
        st.rerun()


def apresentar_saude(bd, codigo, especie):
    aviso = st.session_state.pop("aviso_saude", None)
    if aviso:
        st.success(aviso)

    with st.expander("Registar sintomas"):
        with st.form(f"observar_{codigo}", clear_on_submit=True):
            observada_em = st.date_input("Data da observação", max_value=date.today(), format="DD/MM/YYYY")
            sintomas = st.text_area("Sintomas observados", placeholder="Ex.: manchas nas folhas junto às nervuras")
            if st.form_submit_button("Guardar observação"):
                guardar_acao(bd.observar, "Observação guardada.", codigo, observada_em, sintomas)

    filtro = st.radio("Mostrar ocorrências", ["Ativas", "Fechadas", "Todas"], horizontal=True)
    casos = [
        caso for caso in bd.ocorrencias(codigo)
        if filtro == "Todas" or (caso["fechada_em"] is None) == (filtro == "Ativas")
    ]
    if not casos:
        st.info("Ainda não existem ocorrências para este filtro.")

    opcoes = [chave for chave, ficha in DOENCAS.items()
              if especie.casefold() in {s.casefold() for s in ficha.especies}]
    for caso in casos:
        apresentar_ocorrencia(bd, codigo, caso, opcoes)


def apresentar_ocorrencia(bd, codigo, caso, opcoes):
    ficha = DOENCAS.get(caso["doenca"])
    identificador = caso["id"]
    fecho = caso["fechada_em"]
    inicio = date.fromisoformat(caso["observada_em"])
    dias = ((date.fromisoformat(fecho) if fecho else date.today()) - inicio).days
    with st.container(border=True):
        st.markdown(f"#### {ficha.nome if ficha else 'Por identificar'}")
        estado = "Fechada" if fecho else ("Confirmada" if ficha else "Em dúvida")
        st.caption(f"{estado} · Observada em {formatar_data(caso['observada_em'])} · {dias} dia(s)")
        st.text(caso["sintomas"])
        if fecho:
            st.caption(f"Fechada em {formatar_data(fecho)}")
            if caso["nota_fecho"]:
                st.text(caso["nota_fecho"])
            return

        if ficha is None and opcoes:
            with st.expander("Confirmar doença"):
                with st.form(f"confirmar_{identificador}"):
                    doenca = st.selectbox("Doença", opcoes, index=None, format_func=lambda chave: DOENCAS[chave].nome)
                    if st.form_submit_button("Confirmar identificação"):
                        guardar_acao(bd.confirmar, "Doença confirmada.", codigo, identificador, doenca)
        with st.expander("Fechar ocorrência"):
            with st.form(f"fechar_{identificador}"):
                data = st.date_input("Data de fecho", min_value=inicio, max_value=date.today(), format="DD/MM/YYYY")
                nota = st.text_area("Nota de fecho", placeholder="Opcional")
                if st.form_submit_button("Guardar fecho"):
                    guardar_acao(bd.fechar, "Ocorrência fechada.", codigo, identificador, data, nota)
