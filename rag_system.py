"""
Sistema RAG (Retrieval-Augmented Generation) para el agente de electromagnetismo.
Usa ChromaDB para almacenar y recuperar problemas resueltos.
"""
import os
from typing import List, Dict
import chromadb
from chromadb.config import Settings
import anthropic
from tex_processor import process_all_tex_files


class ElectromagnetismRAG:
    """Sistema RAG para consultas de electromagnetismo."""

    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Inicializa el sistema RAG.

        Args:
            persist_directory: Directorio donde se persiste la base de datos vectorial
        """
        self.persist_directory = persist_directory

        # Inicializar cliente de ChromaDB
        self.chroma_client = chromadb.PersistentClient(path=persist_directory)

        # Crear o cargar colección
        self.collection = self.chroma_client.get_or_create_collection(
            name="electromagnetism_problems",
            metadata={"description": "Problemas resueltos de electromagnetismo"}
        )

        # Inicializar cliente de Anthropic
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY no encontrada en variables de entorno")
        self.anthropic_client = anthropic.Anthropic(api_key=api_key)

    def index_tex_files(self, directory: str = "."):
        """
        Indexa todos los archivos .tex del directorio en la base de datos vectorial.

        Args:
            directory: Directorio donde están los archivos .tex
        """
        print(f"Procesando archivos .tex en {directory}...")
        problems = process_all_tex_files(directory)

        if not problems:
            print("No se encontraron problemas para indexar.")
            return

        print(f"Se encontraron {len(problems)} problemas. Indexando...")

        # Preparar datos para ChromaDB
        documents = []
        metadatas = []
        ids = []

        for i, problem in enumerate(problems):
            documents.append(problem["content"])
            metadatas.append({
                "source": problem["source"],
                "type": problem["type"],
                "problem_number": str(problem["problem_number"])
            })
            ids.append(f"problem_{i}")

        # Agregar a la colección
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

        print(f"✓ {len(problems)} problemas indexados correctamente.")

    def retrieve_relevant_problems(self, query: str, n_results: int = 3) -> List[Dict]:
        """
        Recupera los problemas más relevantes para una consulta.

        Args:
            query: Pregunta o consulta del usuario
            n_results: Número de resultados a retornar

        Returns:
            Lista de problemas relevantes con metadata
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )

        # Formatear resultados
        relevant_problems = []
        if results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                relevant_problems.append({
                    "content": doc,
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                    "distance": results['distances'][0][i] if results['distances'] else None
                })

        return relevant_problems

    def generate_response(self, user_question: str, conversation_history: List[Dict] = None) -> str:
        """
        Genera una respuesta usando Claude con contexto de problemas relevantes.

        Args:
            user_question: Pregunta del usuario
            conversation_history: Historial de conversación previo

        Returns:
            Respuesta generada por Claude
        """
        # Recuperar problemas relevantes
        relevant_problems = self.retrieve_relevant_problems(user_question, n_results=2)

        # Construir contexto
        context = "## Problemas resueltos relevantes:\n\n"
        for i, prob in enumerate(relevant_problems, 1):
            context += f"### Problema {i} - Tipo: {prob['metadata'].get('type', 'N/A')}\n"
            context += f"Fuente: {prob['metadata'].get('source', 'N/A')}\n\n"
            context += f"{prob['content'][:1500]}\n\n"  # Limitar longitud
            context += "---\n\n"

        # Construir prompt del sistema
        system_prompt = """Eres un asistente experto en electromagnetismo para estudiantes de ingeniería.

Tu rol es:
1. Proporcionar respuestas científicamente rigurosas basadas en las ecuaciones de Maxwell y las leyes fundamentales del electromagnetismo
2. Explicar conceptos de forma clara y pedagógica
3. Usar los problemas resueltos como referencia para ayudar al estudiante
4. Mostrar paso a paso las soluciones cuando sea necesario
5. Usar notación matemática clara (LaTeX cuando sea apropiado)

IMPORTANTE:
- Si la pregunta se relaciona con los problemas resueltos proporcionados, úsalos como referencia
- Explica los conceptos físicos detrás de las ecuaciones, no solo des fórmulas
- Si necesitas hacer cálculos, muéstralos paso a paso
- Mantén un tono educativo y de apoyo"""

        # Construir mensaje del usuario con contexto
        user_message = f"{context}\n\n## Pregunta del estudiante:\n{user_question}"

        # Preparar mensajes
        messages = []
        if conversation_history:
            messages.extend(conversation_history)
        messages.append({
            "role": "user",
            "content": user_message
        })

        # Llamar a Claude API
        response = self.anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=system_prompt,
            messages=messages
        )

        return response.content[0].text

    def get_collection_stats(self) -> Dict:
        """Obtiene estadísticas de la colección."""
        count = self.collection.count()
        return {
            "total_problems": count,
            "collection_name": self.collection.name
        }


if __name__ == "__main__":
    # Test del sistema RAG
    from dotenv import load_dotenv
    load_dotenv()

    rag = ElectromagnetismRAG()

    # Indexar archivos si la colección está vacía
    stats = rag.get_collection_stats()
    print(f"Estadísticas: {stats}")

    if stats["total_problems"] == 0:
        print("\nIndexando archivos .tex...")
        rag.index_tex_files("/home/dell/Escritorio/electro_agent")

    # Test de consulta
    print("\n" + "="*50)
    print("Test de consulta")
    print("="*50)

    query = "¿Cómo se calculan capacitores en serie y paralelo?"
    print(f"\nPregunta: {query}")

    response = rag.generate_response(query)
    print(f"\nRespuesta:\n{response}")
