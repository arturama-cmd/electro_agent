"""
Interfaz Streamlit para el agente conversacional de electromagnetismo.
"""
import streamlit as st
import os
from dotenv import load_dotenv
from rag_system import ElectromagnetismRAG

# Cargar variables de entorno
load_dotenv()

# Configuración de la página
st.set_page_config(
    page_title="Asistente de Electromagnetismo",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos personalizados
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .subtitle {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stChatMessage {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def initialize_rag():
    """Inicializa el sistema RAG (se ejecuta una sola vez)."""
    rag = ElectromagnetismRAG()

    # Verificar si necesitamos indexar
    stats = rag.get_collection_stats()
    if stats["total_problems"] == 0:
        with st.spinner("Indexando problemas de electromagnetismo..."):
            rag.index_tex_files("/home/dell/Escritorio/electro_agent")
            st.success("✓ Base de conocimiento inicializada correctamente")

    return rag


def main():
    """Función principal de la aplicación."""

    # Título
    st.markdown('<div class="main-title">⚡ Asistente de Electromagnetismo ⚡</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Tu apoyo inteligente para aprender electromagnetismo</div>', unsafe_allow_html=True)

    # Inicializar sistema RAG
    try:
        rag = initialize_rag()
    except ValueError as e:
        st.error(f"❌ Error de configuración: {e}")
        st.info("💡 Asegúrate de que la variable ANTHROPIC_API_KEY esté configurada en el archivo .env")
        return

    # Sidebar con información
    with st.sidebar:
        st.header("📚 Información")

        stats = rag.get_collection_stats()
        st.metric("Problemas indexados", stats["total_problems"])

        st.markdown("---")

        st.subheader("🎯 ¿Qué puedo hacer?")
        st.markdown("""
        - Responder preguntas sobre electromagnetismo
        - Explicar conceptos de campos eléctricos y magnéticos
        - Ayudarte con problemas de capacitores
        - Resolver circuitos usando leyes de Kirchhoff
        - Aplicar las ecuaciones de Maxwell
        - Mostrar soluciones paso a paso
        """)

        st.markdown("---")

        st.subheader("💡 Ejemplos de preguntas")
        example_questions = [
            "¿Cómo se calculan capacitores en serie?",
            "Explícame la ley de Gauss",
            "¿Qué es el campo eléctrico?",
            "¿Cómo aplico las leyes de Kirchhoff?",
            "¿Cuál es la diferencia entre campo eléctrico y magnético?"
        ]

        for question in example_questions:
            if st.button(question, key=question):
                st.session_state.example_question = question

        st.markdown("---")

        if st.button("🗑️ Limpiar conversación"):
            st.session_state.messages = []
            st.rerun()

    # Inicializar historial de mensajes
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Mostrar mensajes del historial
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Manejar pregunta de ejemplo desde sidebar
    if "example_question" in st.session_state:
        prompt = st.session_state.example_question
        del st.session_state.example_question
    else:
        prompt = st.chat_input("Escribe tu pregunta sobre electromagnetismo...")

    # Procesar nueva pregunta
    if prompt:
        # Agregar mensaje del usuario al historial
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Mostrar mensaje del usuario
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generar respuesta
        with st.chat_message("assistant"):
            with st.spinner("Pensando... 🤔"):
                try:
                    # Preparar historial para Claude (solo últimos 5 intercambios)
                    conversation_history = []
                    for msg in st.session_state.messages[-10:]:  # Últimos 10 mensajes (5 intercambios)
                        if msg["role"] in ["user", "assistant"]:
                            conversation_history.append({
                                "role": msg["role"],
                                "content": msg["content"]
                            })

                    # Generar respuesta
                    response = rag.generate_response(prompt, conversation_history[:-1])  # Excluir el último que ya está en el prompt

                    # Mostrar respuesta
                    st.markdown(response)

                    # Agregar respuesta al historial
                    st.session_state.messages.append({"role": "assistant", "content": response})

                except Exception as e:
                    error_msg = f"❌ Error al generar respuesta: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

    # Footer
    st.markdown("---")
    st.markdown(
        '<div style="text-align: center; color: #666; font-size: 0.9rem;">'
        'Desarrollado con ❤️ usando Claude 4.5, Streamlit y ChromaDB'
        '</div>',
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
