import streamlit as st


def card_metrica(titulo, valor, cor="#1F4E78"):
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, {cor}, #4f8cff);
            padding:20px;
            border-radius:18px;
            box-shadow:0 4px 15px rgba(0,0,0,0.15);
            text-align:center;
            color:white;
            margin-bottom:10px;
        ">
            <h4 style="margin:0; color:white;">{titulo}</h4>
            <h2 style="margin:10px 0 0 0; color:white;">{valor}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )


def secao_titulo(titulo):
    st.markdown(f"## {titulo}")


def caixa_destaque(texto, cor_fundo="#f5f7fb", cor_borda="#1F4E78", cor_texto="#1a1a1a"):
    st.markdown(
        f"""
        <div style="
            background-color:{cor_fundo};
            border-left: 6px solid {cor_borda};
            padding:16px;
            border-radius:10px;
            margin: 10px 0;
            color:{cor_texto};
            font-size:16px;
            line-height:1.6;
            font-weight:500;
        ">
            {texto}
        </div>
        """,
        unsafe_allow_html=True
    )