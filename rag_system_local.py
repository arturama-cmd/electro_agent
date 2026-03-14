"""
Sistema RAG con soporte para modelos locales (Ollama/vLLM) o API de Anthropic.
Configuracion flexible para despliegue universitario.
"""
import os
from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings
from tex_processor import process_all_files_in_category

# Definicion de categorias (temas del curso)
CATEGORIES = {
    "campo_electrico": "Campo Electrico",
    "campo_magnetico": "Campo Magnetico",
    "corriente_directa": "Circuitos en Corriente Directa",
    "corriente_alterna": "Circuitos en Corriente Alterna",
    "maquinas_electricas": "Maquinas Electricas"
}

CORPUS_PATH = "./corpus"

# Configuracion del backend de LLM
LLM_BACKEND = os.getenv("LLM_BACKEND", "anthropic")  # "anthropic", "ollama", "vllm", "openai_compatible"
LOCAL_MODEL_URL = os.getenv("LOCAL_MODEL_URL", "http://localhost:11434")  # URL del servidor local
LOCAL_MODEL_NAME = os.getenv("LOCAL_MODEL_NAME", "llama3.1:70b")  # Modelo a usar


class ElectromagnetismRAG:
    """Sistema RAG para consultas de electromagnetismo con soporte multi-backend."""

    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        self.chroma_client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.chroma_client.get_or_create_collection(
            name="electromagnetism_corpus",
            metadata={"description": "Corpus de electromagnetismo por categorias"}
        )

        # Inicializar cliente segun backend
        self.backend = LLM_BACKEND
        self._init_llm_client()

    def _init_llm_client(self):
        """Inicializa el cliente LLM segun el backend configurado."""
        if self.backend == "anthropic":
            import anthropic
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY no encontrada en variables de entorno")
            self.client = anthropic.Anthropic(api_key=api_key)

        elif self.backend == "ollama":
            # Ollama usa requests directamente o la libreria ollama
            try:
                import ollama
                self.client = ollama.Client(host=LOCAL_MODEL_URL)
            except ImportError:
                import requests
                self.client = None  # Usaremos requests directamente

        elif self.backend == "vllm" or self.backend == "openai_compatible":
            # vLLM y otros servidores compatibles con OpenAI API
            from openai import OpenAI
            self.client = OpenAI(
                base_url=f"{LOCAL_MODEL_URL}/v1",
                api_key="not-needed"  # Modelos locales no requieren API key
            )
        else:
            raise ValueError(f"Backend no soportado: {self.backend}")

    def index_corpus(self, corpus_path: str = CORPUS_PATH):
        """Indexa el corpus de documentos."""
        print(f"Indexando corpus desde {corpus_path}...")
        documents = []
        metadatas = []
        ids = []
        doc_id = 0

        for category_folder, category_name in CATEGORIES.items():
            category_path = os.path.join(corpus_path, category_folder)
            if not os.path.exists(category_path):
                print(f"  Advertencia: Carpeta {category_folder} no existe")
                continue

            print(f"  Procesando categoria: {category_name}")
            chunks = process_all_files_in_category(category_path, category_folder)

            for chunk in chunks:
                documents.append(chunk["content"])
                metadatas.append({
                    "source": chunk["source"],
                    "category": chunk["category"],
                    "category_display": category_name,
                    "chunk_number": chunk["chunk_number"],
                    "file_type": chunk["file_type"]
                })
                ids.append(f"doc_{doc_id}")
                doc_id += 1

        if documents:
            self.collection.add(documents=documents, metadatas=metadatas, ids=ids)
            print(f"Total: {len(documents)} documentos indexados.")
        else:
            print("No se encontraron documentos para indexar.")

    def retrieve_relevant_problems(self, query: str, n_results: int = 3, category_filter: Optional[str] = None) -> List[Dict]:
        """Recupera problemas relevantes del corpus."""
        where_filter = None
        if category_filter and category_filter != "todos":
            where_filter = {"category": category_filter}

        results = self.collection.query(query_texts=[query], n_results=n_results, where=where_filter)

        relevant = []
        if results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                relevant.append({
                    "content": doc,
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i] if results["distances"] else None
                })
        return relevant

    def _generate_with_anthropic(self, messages: List[Dict], system_prompt: str) -> str:
        """Genera respuesta usando API de Anthropic."""
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=system_prompt,
            messages=messages
        )
        return response.content[0].text

    def _generate_with_ollama(self, messages: List[Dict], system_prompt: str) -> str:
        """Genera respuesta usando Ollama (local)."""
        try:
            import ollama
            # Convertir formato de mensajes
            ollama_messages = [{"role": "system", "content": system_prompt}]
            for msg in messages:
                ollama_messages.append({"role": msg["role"], "content": msg["content"]})

            response = self.client.chat(
                model=LOCAL_MODEL_NAME,
                messages=ollama_messages
            )
            return response['message']['content']
        except ImportError:
            # Fallback usando requests
            import requests
            ollama_messages = [{"role": "system", "content": system_prompt}]
            for msg in messages:
                ollama_messages.append({"role": msg["role"], "content": msg["content"]})

            response = requests.post(
                f"{LOCAL_MODEL_URL}/api/chat",
                json={
                    "model": LOCAL_MODEL_NAME,
                    "messages": ollama_messages,
                    "stream": False
                }
            )
            return response.json()['message']['content']

    def _generate_with_openai_compatible(self, messages: List[Dict], system_prompt: str) -> str:
        """Genera respuesta usando servidor compatible con OpenAI API (vLLM, etc.)."""
        openai_messages = [{"role": "system", "content": system_prompt}]
        for msg in messages:
            openai_messages.append({"role": msg["role"], "content": msg["content"]})

        response = self.client.chat.completions.create(
            model=LOCAL_MODEL_NAME,
            messages=openai_messages,
            max_tokens=4096,
            temperature=0.7
        )
        return response.choices[0].message.content

    def generate_response(self, user_question: str, conversation_history: List[Dict] = None, category_filter: Optional[str] = None) -> str:
        """Genera respuesta usando el backend configurado."""
        relevant_docs = self.retrieve_relevant_problems(user_question, n_results=3, category_filter=category_filter)

        context = "## Material de referencia relevante:\n\n"
        for i, doc in enumerate(relevant_docs, 1):
            cat_display = doc["metadata"].get("category_display", "N/A")
            source = doc["metadata"].get("source", "N/A")
            context += f"### Documento {i} - Tema: {cat_display}\n"
            context += f"Fuente: {source}\n\n"
            context += f"{doc['content'][:1500]}\n\n---\n\n"

        system_prompt = """Eres un asistente experto en electromagnetismo para estudiantes de ingenieria.

Tu rol es:
1. Proporcionar respuestas cientificamente rigurosas basadas en las ecuaciones de Maxwell
2. Explicar conceptos de forma clara y pedagogica
3. Usar el material de referencia proporcionado para fundamentar tus respuestas
4. Mostrar paso a paso las soluciones cuando sea necesario
5. Usar notacion matematica clara (LaTeX cuando sea apropiado)

IMPORTANTE:
- Si la pregunta se relaciona con el material de referencia, usalo como base
- Explica los conceptos fisicos detras de las ecuaciones
- Manten un tono educativo y de apoyo"""

        user_message = f"{context}\n\n## Pregunta del estudiante:\n{user_question}"

        messages = []
        if conversation_history:
            messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_message})

        # Seleccionar backend para generacion
        if self.backend == "anthropic":
            return self._generate_with_anthropic(messages, system_prompt)
        elif self.backend == "ollama":
            return self._generate_with_ollama(messages, system_prompt)
        elif self.backend in ["vllm", "openai_compatible"]:
            return self._generate_with_openai_compatible(messages, system_prompt)
        else:
            raise ValueError(f"Backend no soportado: {self.backend}")

    def get_collection_stats(self) -> Dict:
        """Obtiene estadisticas de la coleccion."""
        count = self.collection.count()
        return {"total_problems": count, "collection_name": self.collection.name}

    def get_stats_by_category(self) -> Dict[str, int]:
        """Obtiene estadisticas por categoria."""
        stats = {}
        for category_key in CATEGORIES.keys():
            try:
                results = self.collection.get(where={"category": category_key})
                stats[category_key] = len(results["ids"]) if results["ids"] else 0
            except Exception:
                stats[category_key] = 0
        return stats

    def clear_and_reindex(self, corpus_path: str = CORPUS_PATH):
        """Limpia y reindexa el corpus."""
        existing = self.collection.get()
        if existing["ids"]:
            self.collection.delete(ids=existing["ids"])
        self.index_corpus(corpus_path)


# Informacion del backend actual
def get_backend_info() -> Dict:
    """Retorna informacion sobre el backend configurado."""
    return {
        "backend": LLM_BACKEND,
        "model_url": LOCAL_MODEL_URL if LLM_BACKEND != "anthropic" else "api.anthropic.com",
        "model_name": LOCAL_MODEL_NAME if LLM_BACKEND != "anthropic" else "claude-sonnet-4",
        "is_local": LLM_BACKEND != "anthropic"
    }


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    print(f"Backend configurado: {LLM_BACKEND}")
    print(f"Info: {get_backend_info()}")

    rag = ElectromagnetismRAG()
    stats = rag.get_collection_stats()
    print(f"Estadisticas: {stats}")
