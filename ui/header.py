"""
ui/header.py
Renderiza o cabeçalho superior reutilizável de cada página.
"""
import streamlit as st

import core.state as state


def render_header(titulo: str) -> None:
    inicial = (state.get_user_conta() or "U")[:1].upper()
    c1, c2 = st.columns([5, 1])
    with c1:
        st.markdown(
            f'<h2 style="margin:0; color:#191c1f; font-weight:700;">{titulo}</h2>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""
            <div style="display:flex; align-items:center; justify-content:flex-end;
                        gap:12px; padding-top:4px;">
              <div style="width:34px; height:34px; border-radius:50%;
                          background:#0060ab; color:#fff; display:flex;
                          align-items:center; justify-content:center;
                          font-weight:700; font-size:14px;">{inicial}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown(
        "<hr style='margin-top:8px; margin-bottom:24px;'>",
        unsafe_allow_html=True,
    )
