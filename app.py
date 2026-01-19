"""
Interfaz Streamlit para el agente conversacional de electromagnetismo.
"""
import streamlit as st
import os
from dotenv import load_dotenv
from rag_system import ElectromagnetismRAG, CATEGORIES

# Cargar variables de entorno
load_dotenv()

# Configuracion de la pagina
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
    .category-badge {
        background-color: #1E88E5;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 5px;
        font-size: 0.8rem;
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
        corpus_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "corpus")
        if os.path.exists(corpus_path):
            with st.spinner("Indexando corpus de electromagnetismo..."):
                rag.index_corpus(corpus_path)
                st.success("Base de conocimiento inicializada correctamente")
        else:
            st.warning("Carpeta 'corpus' no encontrada. Crea la estructura de carpetas.")

    return rag


def main():
    """Funcion principal de la aplicacion."""

    # Titulo
    st.markdown('<div class="main-title">⚡ Asistente de Electromagnetismo ⚡</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Tu apoyo inteligente para aprender electromagnetismo</div>', unsafe_allow_html=True)

    # Inicializar sistema RAG
    try:
        rag = initialize_rag()
    except ValueError as e:
        st.error(f"Error de configuracion: {e}")
        st.info("Asegurate de que la variable ANTHROPIC_API_KEY este configurada en el archivo .env")
        return

    # Sidebar con selector de temas
    with st.sidebar:
        st.header("📚 Temas de Estudio")

        # Selector de tema
        tema_options = ["Todos los temas"] + list(CATEGORIES.values())
        tema_keys = ["todos"] + list(CATEGORIES.keys())

        selected_index = st.radio(
            "Selecciona un tema:",
            range(len(tema_options)),
            format_func=lambda x: tema_options[x],
            key="tema_selector"
        )

        selected_category = tema_keys[selected_index]
        st.session_state.selected_category = selected_category

        # Mostrar tema activo
        if selected_category != "todos":
            st.info(f"Consultando: {CATEGORIES[selected_category]}")

        st.markdown("---")

        # Estadisticas por tema
        st.subheader("📊 Documentos por tema")
        stats_by_cat = rag.get_stats_by_category()
        total_docs = sum(stats_by_cat.values())

        for cat_key, cat_name in CATEGORIES.items():
            count = stats_by_cat.get(cat_key, 0)
            st.metric(cat_name, count)

        st.metric("Total", total_docs)

        st.markdown("---")

        # Seccion de administracion
        st.subheader("⚙️ Administracion")

        if st.button("🔄 Reindexar Corpus"):
            with st.spinner("Reindexando..."):
                corpus_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "corpus")
                rag.clear_and_reindex(corpus_path)
                st.cache_resource.clear()
            st.success("Corpus reindexado!")
            st.rerun()

        if st.button("🗑️ Limpiar conversacion"):
            st.session_state.messages = []
            st.rerun()

        st.markdown("---")

        # Ejemplos de preguntas
        st.subheader("💡 Ejemplos de preguntas")
        example_questions = [
            "¿Que es el campo electrico?",
            "Explica la ley de Gauss",
            "¿Como funcionan los capacitores?",
            "¿Que son las leyes de Kirchhoff?",
            "Explica el campo magnetico"
        ]

        for question in example_questions:
            if st.button(question, key=f"ex_{question[:20]}"):
                st.session_state.example_question = question

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
            # Obtener categoria seleccionada
            category_filter = st.session_state.get("selected_category", "todos")

            # Mostrar contexto de busqueda
            if category_filter != "todos":
                st.caption(f"🔍 Buscando en: {CATEGORIES.get(category_filter, category_filter)}")

            with st.spinner("Pensando... 🤔"):
                try:
                    # Preparar historial para Claude
                    conversation_history = []
                    for msg in st.session_state.messages[-10:]:
                        if msg["role"] in ["user", "assistant"]:
                            conversation_history.append({
                                "role": msg["role"],
                                "content": msg["content"]
                            })

                    # Generar respuesta con filtro de categoria
                    response = rag.generate_response(
                        prompt,
                        conversation_history[:-1],
                        category_filter=category_filter
                    )

                    # Mostrar respuesta
                    st.markdown(response)

                    # Agregar respuesta al historial
                    st.session_state.messages.append({"role": "assistant", "content": response})

                except Exception as e:
                    error_msg = f"Error al generar respuesta: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

    # Footer
    st.markdown("---")
    st.markdown(
        '<div style="text-align: center; color: #666; font-size: 0.9rem;">'
        'Desarrollado con Claude, Streamlit y ChromaDB'
        '</div>',
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
