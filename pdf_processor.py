"""
Procesador de archivos PDF para extraccion de texto.
Extrae contenido de PDFs para ser usado en el sistema RAG.
"""
import os
from typing import List, Dict

try:
    import pdfplumber
except ImportError:
    print("pdfplumber no instalado. Ejecuta: pip install pdfplumber")
    pdfplumber = None


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extrae texto de un archivo PDF.
    
    Args:
        file_path: Ruta al archivo PDF
        
    Returns:
        Texto extraido del PDF
    """
    if pdfplumber is None:
        raise ImportError("pdfplumber no esta instalado")
    
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text += f"\n--- Pagina {page_num} ---\n"
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error procesando PDF {file_path}: {e}")
        return ""
    
    return text


def process_pdf_to_chunks(file_path: str, category: str, chunk_size: int = 2000) -> List[Dict]:
    """
    Procesa un PDF y lo divide en chunks para indexacion.
    
    Args:
        file_path: Ruta al PDF
        category: Categoria tematica (carpeta de origen)
        chunk_size: Tamano maximo de cada chunk en caracteres
        
    Returns:
        Lista de diccionarios con metadata de cada chunk
    """
    text = extract_text_from_pdf(file_path)
    
    if not text.strip():
        return []
    
    filename = os.path.basename(file_path)
    chunks = []
    
    # Dividir por paginas primero
    pages = text.split("--- Pagina ")
    
    for i, page_content in enumerate(pages):
        if not page_content.strip():
            continue
            
        # Limpiar el marcador de pagina
        page_content = page_content.strip()
        if page_content.startswith("---"):
            # Quitar la linea del marcador
            lines = page_content.split("\n", 1)
            if len(lines) > 1:
                page_content = lines[1]
        
        if not page_content.strip():
            continue
        
        # Si la pagina es muy grande, subdividir
        if len(page_content) > chunk_size:
            # Dividir por parrafos o por tamano
            sub_chunks = []
            current_chunk = ""
            
            for paragraph in page_content.split("\n\n"):
                if len(current_chunk) + len(paragraph) < chunk_size:
                    current_chunk += paragraph + "\n\n"
                else:
                    if current_chunk.strip():
                        sub_chunks.append(current_chunk.strip())
                    current_chunk = paragraph + "\n\n"
            
            if current_chunk.strip():
                sub_chunks.append(current_chunk.strip())
            
            for k, sub in enumerate(sub_chunks):
                chunks.append({
                    "source": filename,
                    "category": category,
                    "chunk_number": f"{i}_{k}",
                    "content": sub,
                    "file_type": "pdf"
                })
        else:
            chunks.append({
                "source": filename,
                "category": category,
                "chunk_number": str(i),
                "content": page_content.strip(),
                "file_type": "pdf"
            })
    
    return chunks


if __name__ == "__main__":
    # Test del procesador
    import sys
    
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        print(f"Procesando: {pdf_path}")
        chunks = process_pdf_to_chunks(pdf_path, "test_category")
        print(f"Se extrajeron {len(chunks)} chunks")
        for i, chunk in enumerate(chunks[:2]):
            print(f"\n{'='*50}")
            print(f"Chunk {i+1}")
            print(f"Source: {chunk['source']}")
            print(f"Category: {chunk['category']}")
            print(f"Content (primeros 300 chars):\n{chunk['content'][:300]}")
    else:
        print("Uso: python pdf_processor.py <ruta_al_pdf>")
