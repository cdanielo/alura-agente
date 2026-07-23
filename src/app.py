import streamlit as st
from agent import cargar_agente, preguntar

st.set_page_config(page_title="Alura Agente — Santos Pegasus Soluciones", page_icon="🤖")

st.title("🤖 Alura Agente")
st.caption("Asistente interno de documentación — Santos Pegasus Soluciones")

st.markdown(
    "Pregunta lo que quieras sobre el Manual de Onboarding, la Guía de "
    "Ingeniería Back-end/Front-end, el Protocolo de Incidentes o la "
    "Arquitectura de Microservicios."
)


@st.cache_resource(show_spinner="Cargando el agente (esto solo pasa una vez)...")
def get_chain():
    return cargar_agente()


try:
    chain = get_chain()
except Exception as e:
    st.error(f"No se pudo cargar el agente: {e}")
    st.stop()

if "historial" not in st.session_state:
    st.session_state.historial = []

for pregunta, respuesta, fuentes in st.session_state.historial:
    with st.chat_message("user"):
        st.write(pregunta)
    with st.chat_message("assistant"):
        st.write(respuesta)
        st.caption(f"Fuente(s): {', '.join(fuentes)}")

pregunta = st.chat_input("Escribe tu pregunta...")

if pregunta:
    with st.chat_message("user"):
        st.write(pregunta)

    with st.chat_message("assistant"):
        with st.spinner("Buscando en la documentación..."):
            respuesta, fuentes = preguntar(chain, pregunta)
        st.write(respuesta)
        st.caption(f"Fuente(s): {', '.join(fuentes)}")

    st.session_state.historial.append((pregunta, respuesta, fuentes))
