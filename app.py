"""
Interfaz Streamlit Mobile-First para el asistente de electromagnetismo.
Diseño moderno, liviano y optimizado para dispositivos moviles.
"""
import streamlit as st
import os
import tempfile
from dotenv import load_dotenv
from rag_system import ElectromagnetismRAG, CATEGORIES
from pdf_processor import process_pdf_to_chunks

load_dotenv()

# Configuracion de pagina - Mobile First
st.set_page_config(
    page_title="ElectroAI",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS Mobile-First Moderno
st.markdown("""
<style>
    /* Reset y variables */
    :root {
        --primary: #6366f1;
        --primary-dark: #4f46e5;
        --secondary: #10b981;
        --accent: #f59e0b;
        --bg-dark: #0f172a;
        --bg-card: #1e293b;
        --text-primary: #f1f5f9;
        --text-secondary: #94a3b8;
        --border-radius: 16px;
        --shadow: 0 4px 20px rgba(0,0,0,0.3);
    }

    /* Ocultar elementos de Streamlit */
    #MainMenu, footer, header {visibility: hidden;}
    .stDeployButton {display: none;}

    /* Fondo principal */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    }

    /* Container principal */
    .main .block-container {
        padding: 0.5rem 1rem 5rem 1rem;
        max-width: 100%;
    }

    /* Header compacto */
    .app-header {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
        border-radius: 0 0 24px 24px;
        padding: 1rem;
        margin: -1rem -1rem 1rem -1rem;
        text-align: center;
        box-shadow: var(--shadow);
    }

    .app-logo {
        font-size: 2rem;
        margin-bottom: 0.25rem;
    }

    .app-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: white;
        margin: 0;
        letter-spacing: -0.5px;
    }

    .app-subtitle {
        font-size: 0.8rem;
        color: rgba(255,255,255,0.8);
        margin: 0;
    }

    /* Navegacion inferior */
    .bottom-nav {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: var(--bg-card);
        border-top: 1px solid rgba(255,255,255,0.1);
        display: flex;
        justify-content: space-around;
        padding: 0.5rem 0;
        z-index: 1000;
        backdrop-filter: blur(10px);
    }

    .nav-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 0.5rem 1.5rem;
        border-radius: 12px;
        cursor: pointer;
        transition: all 0.2s ease;
        color: var(--text-secondary);
        text-decoration: none;
    }

    .nav-item.active {
        background: var(--primary);
        color: white;
    }

    .nav-icon {
        font-size: 1.5rem;
        margin-bottom: 0.2rem;
    }

    .nav-label {
        font-size: 0.7rem;
        font-weight: 500;
    }

    /* Cards */
    .card {
        background: var(--bg-card);
        border-radius: var(--border-radius);
        padding: 1.25rem;
        margin-bottom: 1rem;
        box-shadow: var(--shadow);
        border: 1px solid rgba(255,255,255,0.05);
    }

    .card-title {
        font-size: 1rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* Botones modernos */
    .btn-primary {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.875rem 1.5rem;
        font-weight: 600;
        font-size: 0.95rem;
        width: 100%;
        cursor: pointer;
        transition: all 0.2s ease;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
    }

    .btn-primary:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.5);
    }

    .btn-secondary {
        background: transparent;
        color: var(--primary);
        border: 2px solid var(--primary);
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 0.9rem;
        cursor: pointer;
        transition: all 0.2s ease;
    }

    .btn-success {
        background: linear-gradient(135deg, var(--secondary) 0%, #059669 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.875rem 1.5rem;
        font-weight: 600;
        width: 100%;
        cursor: pointer;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);
    }

    /* Chat bubbles */
    .chat-container {
        max-height: 55vh;
        overflow-y: auto;
        padding: 0.5rem;
        margin-bottom: 1rem;
    }

    .chat-bubble {
        max-width: 85%;
        padding: 0.875rem 1rem;
        border-radius: 18px;
        margin-bottom: 0.75rem;
        font-size: 0.9rem;
        line-height: 1.5;
        animation: fadeIn 0.3s ease;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .chat-user {
        background: var(--primary);
        color: white;
        margin-left: auto;
        border-bottom-right-radius: 4px;
    }

    .chat-assistant {
        background: var(--bg-card);
        color: var(--text-primary);
        border: 1px solid rgba(255,255,255,0.1);
        border-bottom-left-radius: 4px;
    }

    .chat-time {
        font-size: 0.65rem;
        color: var(--text-secondary);
        margin-top: 0.25rem;
    }

    /* Input chat */
    .chat-input-container {
        position: relative;
        margin-top: auto;
    }

    /* Quick actions */
    .quick-actions {
        display: flex;
        gap: 0.5rem;
        overflow-x: auto;
        padding: 0.5rem 0;
        margin-bottom: 1rem;
        -webkit-overflow-scrolling: touch;
    }

    .quick-action {
        flex-shrink: 0;
        background: var(--bg-card);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 20px;
        padding: 0.5rem 1rem;
        font-size: 0.8rem;
        color: var(--text-secondary);
        cursor: pointer;
        transition: all 0.2s ease;
        white-space: nowrap;
    }

    .quick-action:hover {
        background: var(--primary);
        color: white;
        border-color: var(--primary);
    }

    /* Topic pills */
    .topic-pills {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-bottom: 1rem;
    }

    .topic-pill {
        background: rgba(99, 102, 241, 0.2);
        color: var(--primary);
        border-radius: 20px;
        padding: 0.4rem 0.875rem;
        font-size: 0.75rem;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s ease;
        border: 1px solid transparent;
    }

    .topic-pill.active {
        background: var(--primary);
        color: white;
    }

    .topic-pill:hover {
        border-color: var(--primary);
    }

    /* Upload zone */
    .upload-zone {
        border: 2px dashed rgba(99, 102, 241, 0.5);
        border-radius: var(--border-radius);
        padding: 2rem;
        text-align: center;
        background: rgba(99, 102, 241, 0.05);
        transition: all 0.2s ease;
        cursor: pointer;
    }

    .upload-zone:hover {
        border-color: var(--primary);
        background: rgba(99, 102, 241, 0.1);
    }

    .upload-icon {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }

    .upload-text {
        color: var(--text-secondary);
        font-size: 0.9rem;
    }

    /* Stats mini */
    .stats-row {
        display: flex;
        gap: 0.75rem;
        margin-bottom: 1rem;
    }

    .stat-mini {
        flex: 1;
        background: var(--bg-card);
        border-radius: 12px;
        padding: 0.75rem;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.05);
    }

    .stat-value {
        font-size: 1.25rem;
        font-weight: 700;
        color: var(--primary);
    }

    .stat-label {
        font-size: 0.65rem;
        color: var(--text-secondary);
        text-transform: uppercase;
    }

    /* Solver section */
    .solver-input {
        background: var(--bg-card);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 1rem;
        color: var(--text-primary);
        font-size: 0.9rem;
        width: 100%;
        min-height: 150px;
        resize: none;
    }

    .solver-input:focus {
        outline: none;
        border-color: var(--primary);
    }

    /* Animations */
    .pulse {
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }

    /* Scrollbar personalizado */
    ::-webkit-scrollbar {
        width: 4px;
        height: 4px;
    }

    ::-webkit-scrollbar-track {
        background: transparent;
    }

    ::-webkit-scrollbar-thumb {
        background: var(--primary);
        border-radius: 4px;
    }

    /* Override Streamlit widgets */
    .stTextInput > div > div > input {
        background: var(--bg-card) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 12px !important;
        color: var(--text-primary) !important;
        padding: 0.75rem 1rem !important;
    }

    .stTextArea > div > div > textarea {
        background: var(--bg-card) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 12px !important;
        color: var(--text-primary) !important;
    }

    .stSelectbox > div > div {
        background: var(--bg-card) !important;
        border-radius: 12px !important;
    }

    .stButton > button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        width: 100% !important;
        transition: all 0.2s ease !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.5) !important;
    }

    /* File uploader */
    .stFileUploader > div {
        background: transparent !important;
    }

    .stFileUploader > div > div {
        background: rgba(99, 102, 241, 0.05) !important;
        border: 2px dashed rgba(99, 102, 241, 0.5) !important;
        border-radius: 16px !important;
    }

    /* Radio buttons como pills */
    .stRadio > div {
        flex-direction: row !important;
        flex-wrap: wrap !important;
        gap: 0.5rem !important;
    }

    .stRadio > div > label {
        background: var(--bg-card) !important;
        border-radius: 20px !important;
        padding: 0.5rem 1rem !important;
        margin: 0 !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
    }

    .stRadio > div > label[data-checked="true"] {
        background: var(--primary) !important;
        border-color: var(--primary) !important;
    }

    /* Spinner */
    .stSpinner > div {
        border-color: var(--primary) !important;
    }

    /* Success/Error messages */
    .stSuccess {
        background: rgba(16, 185, 129, 0.1) !important;
        border: 1px solid var(--secondary) !important;
        border-radius: 12px !important;
    }

    .stError {
        background: rgba(239, 68, 68, 0.1) !important;
        border: 1px solid #ef4444 !important;
        border-radius: 12px !important;
    }

    /* Tabs personalizados */
    .stTabs [data-baseweb="tab-list"] {
        background: var(--bg-card);
        border-radius: 12px;
        padding: 0.25rem;
        gap: 0.25rem;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        color: var(--text-secondary);
        font-weight: 500;
    }

    .stTabs [aria-selected="true"] {
        background: var(--primary) !important;
        color: white !important;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background: var(--bg-card) !important;
        border-radius: 12px !important;
        color: var(--text-primary) !important;
    }

    /* Hide default chat styling */
    .stChatMessage {
        background: transparent !important;
        padding: 0 !important;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def initialize_rag():
    """Inicializa el sistema RAG."""
    rag = ElectromagnetismRAG()
    stats = rag.get_collection_stats()
    if stats["total_problems"] == 0:
        corpus_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "corpus")
        if os.path.exists(corpus_path):
            rag.index_corpus(corpus_path)
    return rag


def render_header():
    """Renderiza el header de la app."""
    st.markdown("""
    <div class="app-header">
        <div class="app-logo">⚡</div>
        <h1 class="app-title">ElectroAI</h1>
        <p class="app-subtitle">Tu asistente de electromagnetismo</p>
    </div>
    """, unsafe_allow_html=True)


def render_stats(rag):
    """Renderiza estadisticas mini."""
    stats = rag.get_stats_by_category()
    total = sum(stats.values())

    st.markdown(f"""
    <div class="stats-row">
        <div class="stat-mini">
            <div class="stat-value">{stats.get('campo_electrico', 0)}</div>
            <div class="stat-label">Campo E</div>
        </div>
        <div class="stat-mini">
            <div class="stat-value">{stats.get('campo_magnetico', 0)}</div>
            <div class="stat-label">Campo B</div>
        </div>
        <div class="stat-mini">
            <div class="stat-value">{total}</div>
            <div class="stat-label">Total</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_chat_view(rag):
    """Vista de Chat."""
    # Selector de tema compacto
    st.markdown('<div class="card-title">📚 Tema</div>', unsafe_allow_html=True)

    tema_options = ["Todos"] + list(CATEGORIES.values())
    tema_keys = ["todos"] + list(CATEGORIES.keys())

    selected = st.radio(
        "Filtrar por tema:",
        range(len(tema_options)),
        format_func=lambda x: tema_options[x],
        horizontal=True,
        label_visibility="collapsed"
    )
    st.session_state.selected_category = tema_keys[selected]

    st.markdown("<br>", unsafe_allow_html=True)

    # Quick actions
    st.markdown('<div class="card-title">💡 Preguntas rapidas</div>', unsafe_allow_html=True)

    quick_questions = [
        "Ley de Coulomb",
        "Campo electrico",
        "Ley de Gauss",
        "Fuerza magnetica",
        "Ley de Biot-Savart"
    ]

    cols = st.columns(len(quick_questions))
    for i, q in enumerate(quick_questions):
        if cols[i].button(q, key=f"quick_{i}", use_container_width=True):
            st.session_state.quick_question = f"Explicame {q}"

    st.markdown("<br>", unsafe_allow_html=True)

    # Chat container
    st.markdown('<div class="card-title">💬 Conversacion</div>', unsafe_allow_html=True)

    # Inicializar mensajes
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Mostrar mensajes
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-bubble chat-user">{msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-bubble chat-assistant">{msg["content"]}</div>', unsafe_allow_html=True)

    # Input de chat
    st.markdown("<br>", unsafe_allow_html=True)

    # Manejar quick question
    if "quick_question" in st.session_state:
        prompt = st.session_state.quick_question
        del st.session_state.quick_question
    else:
        prompt = st.chat_input("Escribe tu pregunta...")

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.spinner("Pensando..."):
            try:
                category_filter = st.session_state.get("selected_category", "todos")
                conversation_history = [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages[-10:]
                    if m["role"] in ["user", "assistant"]
                ]

                response = rag.generate_response(
                    prompt,
                    conversation_history[:-1],
                    category_filter=category_filter
                )
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
            except Exception as e:
                st.error(f"Error: {str(e)}")

    # Boton limpiar chat
    if st.session_state.messages:
        if st.button("🗑️ Limpiar chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()


def render_solver_view(rag):
    """Vista del Solucionador de Problemas."""
    st.markdown('<div class="card-title">🧮 Solucionador de Problemas</div>', unsafe_allow_html=True)

    st.markdown("""
    <p style="color: var(--text-secondary); font-size: 0.85rem; margin-bottom: 1rem;">
        Ingresa un problema de electromagnetismo y obtendras una solucion paso a paso.
    </p>
    """, unsafe_allow_html=True)

    # Selector de tipo de problema
    problem_type = st.selectbox(
        "Tipo de problema:",
        ["Campo Electrico", "Campo Magnetico", "Circuitos DC", "Circuitos AC"],
        label_visibility="visible"
    )

    # Area de texto para el problema
    problem_text = st.text_area(
        "Describe el problema:",
        placeholder="Ejemplo: Tres cargas puntuales q1=2μC, q2=-3μC y q3=4μC estan ubicadas en los vertices de un triangulo equilatero de lado 10cm. Calcular la fuerza neta sobre q1.",
        height=150,
        label_visibility="visible"
    )

    # Opcion de subir imagen del problema
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("📷 Adjuntar imagen del problema (opcional)"):
        uploaded_image = st.file_uploader(
            "Sube una foto del problema",
            type=["png", "jpg", "jpeg"],
            label_visibility="collapsed"
        )
        if uploaded_image:
            st.image(uploaded_image, caption="Imagen del problema", use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Boton resolver
    if st.button("⚡ Resolver Problema", use_container_width=True, type="primary"):
        if problem_text.strip():
            with st.spinner("Analizando y resolviendo..."):
                try:
                    # Construir prompt para solucion
                    solver_prompt = f"""Resuelve el siguiente problema de {problem_type} paso a paso:

{problem_text}

Por favor proporciona:
1. Datos del problema identificados
2. Diagrama o esquema (descripcion)
3. Analisis cualitativo
4. Desarrollo matematico completo
5. Resultado final con unidades
6. Interpretacion fisica del resultado"""

                    category_map = {
                        "Campo Electrico": "campo_electrico",
                        "Campo Magnetico": "campo_magnetico",
                        "Circuitos DC": "corriente_directa",
                        "Circuitos AC": "corriente_alterna"
                    }

                    response = rag.generate_response(
                        solver_prompt,
                        [],
                        category_filter=category_map.get(problem_type, "todos")
                    )

                    st.markdown("---")
                    st.markdown('<div class="card-title">📝 Solucion</div>', unsafe_allow_html=True)
                    st.markdown(response)

                    # Opcion de enviar al chat
                    if st.button("💬 Continuar en Chat", use_container_width=True):
                        st.session_state.messages.append({"role": "user", "content": problem_text})
                        st.session_state.messages.append({"role": "assistant", "content": response})
                        st.session_state.active_tab = "Chat"
                        st.rerun()

                except Exception as e:
                    st.error(f"Error al resolver: {str(e)}")
        else:
            st.warning("Por favor ingresa un problema para resolver.")


def render_upload_view(rag):
    """Vista para subir problemas al corpus."""
    st.markdown('<div class="card-title">📤 Subir Problemas</div>', unsafe_allow_html=True)

    st.markdown("""
    <p style="color: var(--text-secondary); font-size: 0.85rem; margin-bottom: 1rem;">
        Agrega nuevos problemas y soluciones a la base de conocimiento.
    </p>
    """, unsafe_allow_html=True)

    # Selector de categoria
    category = st.selectbox(
        "Categoria:",
        list(CATEGORIES.keys()),
        format_func=lambda x: CATEGORIES[x]
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Tabs para diferentes tipos de subida
    upload_tab1, upload_tab2 = st.tabs(["📄 Archivo PDF/TEX", "✍️ Texto manual"])

    with upload_tab1:
        st.markdown("""
        <div class="upload-zone">
            <div class="upload-icon">📁</div>
            <div class="upload-text">Arrastra archivos aqui o haz clic para seleccionar</div>
        </div>
        """, unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            "Selecciona archivo",
            type=["pdf", "tex"],
            label_visibility="collapsed"
        )

        if uploaded_file:
            st.success(f"Archivo: {uploaded_file.name}")

            if st.button("⬆️ Subir al Corpus", use_container_width=True, type="primary"):
                with st.spinner("Procesando archivo..."):
                    try:
                        # Guardar temporalmente
                        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
                            tmp.write(uploaded_file.getvalue())
                            tmp_path = tmp.name

                        # Procesar segun tipo
                        if uploaded_file.name.lower().endswith('.pdf'):
                            chunks = process_pdf_to_chunks(tmp_path, category)
                        else:
                            from tex_processor import extract_chunks_from_tex
                            chunks = extract_chunks_from_tex(tmp_path, category)

                        if chunks:
                            # Agregar a ChromaDB
                            collection = rag.collection
                            existing = collection.get()
                            next_id = max([int(id.replace("doc_", "")) for id in existing["ids"]] or [0]) + 1

                            documents = [c["content"] for c in chunks]
                            metadatas = [{
                                "source": uploaded_file.name,
                                "category": category,
                                "category_display": CATEGORIES[category],
                                "chunk_number": c["chunk_number"],
                                "file_type": c["file_type"]
                            } for c in chunks]
                            ids = [f"doc_{next_id + i}" for i in range(len(chunks))]

                            collection.add(documents=documents, metadatas=metadatas, ids=ids)
                            st.success(f"Se agregaron {len(chunks)} fragmentos al corpus.")
                        else:
                            st.warning("No se pudo extraer contenido del archivo.")

                        # Limpiar temporal
                        os.unlink(tmp_path)

                    except Exception as e:
                        st.error(f"Error: {str(e)}")

    with upload_tab2:
        problem_title = st.text_input("Titulo del problema:", placeholder="Ej: Fuerza entre cargas puntuales")

        problem_content = st.text_area(
            "Contenido (problema y solucion):",
            placeholder="Escribe el enunciado del problema y su solucion completa...",
            height=250
        )

        if st.button("💾 Guardar Problema", use_container_width=True, type="primary"):
            if problem_title and problem_content:
                with st.spinner("Guardando..."):
                    try:
                        collection = rag.collection
                        existing = collection.get()
                        next_id = max([int(id.replace("doc_", "")) for id in existing["ids"]] or [0]) + 1

                        collection.add(
                            documents=[problem_content],
                            metadatas=[{
                                "source": f"{problem_title}.manual",
                                "category": category,
                                "category_display": CATEGORIES[category],
                                "chunk_number": "0",
                                "file_type": "manual"
                            }],
                            ids=[f"doc_{next_id}"]
                        )
                        st.success("Problema guardado exitosamente.")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            else:
                st.warning("Completa todos los campos.")

    # Estadisticas del corpus
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="card-title">📊 Estado del Corpus</div>', unsafe_allow_html=True)
    render_stats(rag)

    # Boton reindexar
    with st.expander("⚙️ Opciones avanzadas"):
        if st.button("🔄 Reindexar todo el corpus", use_container_width=True):
            with st.spinner("Reindexando..."):
                corpus_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "corpus")
                rag.clear_and_reindex(corpus_path)
                st.cache_resource.clear()
            st.success("Corpus reindexado!")
            st.rerun()


def main():
    """Funcion principal."""
    # Inicializar RAG
    try:
        rag = initialize_rag()
    except ValueError as e:
        st.error(f"Error: {e}")
        st.info("Configura ANTHROPIC_API_KEY en el archivo .env")
        return

    # Header
    render_header()

    # Tabs como navegacion principal
    tab1, tab2, tab3 = st.tabs(["💬 Chat", "🧮 Resolver", "📤 Subir"])

    with tab1:
        render_chat_view(rag)

    with tab2:
        render_solver_view(rag)

    with tab3:
        render_upload_view(rag)

    # Footer minimalista
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0 4rem 0; color: var(--text-secondary); font-size: 0.75rem;">
        ElectroAI v2.0 | UBB
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
