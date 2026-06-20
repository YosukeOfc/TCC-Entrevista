"""
ui/pages/auth.py
Tela de login e cadastro de usuários.
"""
import streamlit as st

import core.state as state
from services import auth_service


def render() -> None:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(
            """
            <div style="text-align:center; margin-bottom:32px;">
              <div style="font-size:42px; margin-bottom:8px;">💼</div>
              <h1 style="font-size:2rem; font-weight:700; color:#191c1f; margin:0;">
                InterviewAI
              </h1>
              <p style="color:#5b403e; margin-top:8px;">
                Entre ou crie sua conta para acessar suas entrevistas
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        tab_login, tab_cadastro = st.tabs(["Entrar", "Cadastrar"])

        with tab_login:
            _form_login()

        with tab_cadastro:
            _form_cadastro()


def _form_login() -> None:
    with st.form("form_login", clear_on_submit=False):
        email = st.text_input("E-mail", placeholder="seu@email.com", key="login_email")
        senha = st.text_input(
            "Senha",
            type="password",
            placeholder="Digite sua senha",
            key="login_senha",
        )
        enviar = st.form_submit_button(
            "Entrar",
            use_container_width=True,
            type="primary",
        )

    if enviar:
        usuario, erro = auth_service.autenticar_usuario(email, senha)
        if erro:
            st.error(erro)
            return
        state.login(usuario)
        st.rerun()


def _form_cadastro() -> None:
    with st.form("form_cadastro", clear_on_submit=False):
        conta = st.text_input("Conta", placeholder="nome_de_usuario", key="cadastro_conta")
        email = st.text_input("E-mail", placeholder="seu@email.com", key="cadastro_email")
        senha = st.text_input(
            "Senha",
            type="password",
            placeholder="Mínimo 6 caracteres",
            key="cadastro_senha",
        )
        confirmar = st.text_input(
            "Confirmar senha",
            type="password",
            placeholder="Repita sua senha",
            key="cadastro_confirmar",
        )
        enviar = st.form_submit_button(
            "Criar conta",
            use_container_width=True,
            type="primary",
        )

    if enviar:
        if senha != confirmar:
            st.error("As senhas não coincidem.")
            return
        usuario, erro = auth_service.cadastrar_usuario(conta, email, senha)
        if erro:
            st.error(erro)
            return
        state.login(usuario)
        st.success("Conta criada com sucesso!")
        st.rerun()
