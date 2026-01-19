"""
Sistema RAG (Retrieval-Augmented Generation) para el agente de electromagnetismo.
Usa ChromaDB para almacenar y recuperar documentos por categorias.
"""
import os
from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings
import anthropic
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


class ElectromagnetismRAG:
    """Sistema RAG para consultas de electromagnetismo."""

    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        self.chroma_client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.chroma_client.get_or_create_collection(
            name="electromagnetism_corpus",
            metadata={"description": "Corpus de electromagnetismo por categorias"}
        )
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY no encontrada en variables de entorno")
        self.anthropic_client = anthropic.Anthropic(api_key=api_key)

    def index_corpus(self, corpus_path: str = CORPUS_PATH):
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

    def generate_response(self, user_question: str, conversation_history: List[Dict] = None, category_filter: Optional[str] = None) -> str:
        relevant_docs = self.retrieve_relevant_problems(user_question, n_results=3, category_filter=category_filter)

        context = "## Material de referencia relevante:

"
        for i, doc in enumerate(relevant_docs, 1):
            cat_display = doc["metadata"].get("category_display", "N/A")
            source = doc["metadata"].get("source", "N/A")
            context += f"### Documento {i} - Tema: {cat_display}
"
            context += f"Fuente: {source}

"
            context += f"{doc['content'][:1500]}

---

"

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

        user_message = f"{context}

## Pregunta del estudiante:
{user_question}"

        messages = []
        if conversation_history:
            messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_message})

        response = self.anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=system_prompt,
            messages=messages
        )
        return response.content[0].text

    def get_collection_stats(self) -> Dict:
        count = self.collection.count()
        return {"total_problems": count, "collection_name": self.collection.name}

    def get_stats_by_category(self) -> Dict[str, int]:
        stats = {}
        for category_key in CATEGORIES.keys():
            try:
                results = self.collection.get(where={"category": category_key})
                stats[category_key] = len(results["ids"]) if results["ids"] else 0
            except Exception:
                stats[category_key] = 0
        return stats

    def clear_and_reindex(self, corpus_path: str = CORPUS_PATH):
        existing = self.collection.get()
        if existing["ids"]:
            self.collection.delete(ids=existing["ids"])
        self.index_corpus(corpus_path)

    def index_tex_files(self, directory: str = "."):
        self.index_corpus(directory)


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    rag = ElectromagnetismRAG()
    stats = rag.get_collection_stats()
    print(f"Estadisticas: {stats}")
