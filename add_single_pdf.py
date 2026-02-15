"""
Script para agregar un solo archivo PDF al ChromaDB existente.
"""
import os
import chromadb
from pdf_processor import process_pdf_to_chunks

def add_pdf_to_collection(pdf_path: str, category: str):
    """Agrega un PDF específico a la colección de ChromaDB."""

    # Conectar a ChromaDB existente
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    collection = chroma_client.get_or_create_collection(
        name="electromagnetism_corpus",
        metadata={"description": "Corpus de electromagnetismo por categorias"}
    )

    # Obtener el ID máximo actual para continuar la numeración
    existing = collection.get()
    if existing["ids"]:
        max_id = max(int(id.replace("doc_", "")) for id in existing["ids"])
        next_id = max_id + 1
    else:
        next_id = 0

    print(f"Procesando: {pdf_path}")
    print(f"Categoría: {category}")
    print(f"ID inicial: doc_{next_id}")

    # Procesar el PDF
    chunks = process_pdf_to_chunks(pdf_path, category)

    if not chunks:
        print("No se extrajeron chunks del PDF.")
        return

    # Preparar datos para ChromaDB
    documents = []
    metadatas = []
    ids = []

    # Mapeo de categorías
    CATEGORIES = {
        "campo_electrico": "Campo Electrico",
        "campo_magnetico": "Campo Magnetico",
        "corriente_directa": "Circuitos en Corriente Directa",
        "corriente_alterna": "Circuitos en Corriente Alterna",
        "maquinas_electricas": "Maquinas Electricas"
    }

    category_display = CATEGORIES.get(category, category)

    for chunk in chunks:
        documents.append(chunk["content"])
        metadatas.append({
            "source": chunk["source"],
            "category": category,
            "category_display": category_display,
            "chunk_number": chunk["chunk_number"],
            "file_type": chunk["file_type"]
        })
        ids.append(f"doc_{next_id}")
        next_id += 1

    # Agregar a la colección
    collection.add(documents=documents, metadatas=metadatas, ids=ids)

    print(f"\nAgregados {len(documents)} chunks a la colección.")
    print(f"Total en colección: {collection.count()}")


if __name__ == "__main__":
    # Agregar el PDF de Sears
    pdf_path = "./corpus/campo_electrico/campo electrico sears.pdf"
    category = "campo_electrico"

    if not os.path.exists(pdf_path):
        print(f"Error: No se encontró el archivo: {pdf_path}")
    else:
        add_pdf_to_collection(pdf_path, category)
