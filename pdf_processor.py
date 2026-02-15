"""
Procesador de archivos PDF para extraccion de texto.
Extrae contenido de PDFs para ser usado en el sistema RAG.
Soporta PDFs con texto y PDFs escaneados (OCR).
"""
import os
from typing import List, Dict

try:
    import pdfplumber
except ImportError:
    print("pdfplumber no instalado. Ejecuta: pip install pdfplumber")
    pdfplumber = None

# OCR dependencies (optional)
try:
    import pytesseract
    from pdf2image import convert_from_path
    from PIL import Image
    OCR_AVAILABLE = True

    # Configure Tesseract path for Windows
    import platform
    if platform.system() == "Windows":
        tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        if os.path.exists(tesseract_path):
            pytesseract.pytesseract.tesseract_cmd = tesseract_path

        # Use local tessdata directory if available (for additional languages)
        local_tessdata = os.path.join(os.path.dirname(__file__), "tessdata")
        if os.path.exists(local_tessdata):
            os.environ["TESSDATA_PREFIX"] = local_tessdata

    # Configure Poppler path for Windows (local installation)
    POPPLER_PATH = None
    if platform.system() == "Windows":
        # Check local poppler installation first
        local_poppler = os.path.join(os.path.dirname(__file__), "poppler-24.08.0", "Library", "bin")
        if os.path.exists(local_poppler):
            POPPLER_PATH = local_poppler
except ImportError:
    OCR_AVAILABLE = False
    pytesseract = None
    POPPLER_PATH = None


def extract_text_with_ocr(file_path: str, language: str = "spa") -> str:
    """
    Extrae texto de un PDF escaneado usando OCR (Tesseract).

    Args:
        file_path: Ruta al archivo PDF
        language: Idioma para OCR (spa=espanol, eng=ingles)

    Returns:
        Texto extraido mediante OCR
    """
    if not OCR_AVAILABLE:
        raise ImportError("pytesseract y pdf2image no estan instalados. Ejecuta: pip install pytesseract pdf2image")

    text = ""
    try:
        # Convertir PDF a imagenes (una por pagina)
        print(f"  Convirtiendo PDF a imagenes para OCR...")
        if POPPLER_PATH:
            images = convert_from_path(file_path, dpi=300, poppler_path=POPPLER_PATH)
        else:
            images = convert_from_path(file_path, dpi=300)

        for page_num, image in enumerate(images, 1):
            print(f"    OCR pagina {page_num}/{len(images)}...")
            page_text = pytesseract.image_to_string(image, lang=language)
            if page_text.strip():
                text += f"\n--- Pagina {page_num} ---\n"
                text += page_text + "\n"

    except Exception as e:
        print(f"Error en OCR para {file_path}: {e}")
        return ""

    return text


def extract_text_from_pdf(file_path: str, use_ocr_fallback: bool = True) -> str:
    """
    Extrae texto de un archivo PDF.
    Primero intenta extraccion directa, si falla usa OCR.

    Args:
        file_path: Ruta al archivo PDF
        use_ocr_fallback: Si True, usa OCR cuando no hay texto extraible

    Returns:
        Texto extraido del PDF
    """
    if pdfplumber is None:
        raise ImportError("pdfplumber no esta instalado")

    text = ""
    has_text = False

    try:
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    has_text = True
                    text += f"\n--- Pagina {page_num} ---\n"
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error procesando PDF {file_path}: {e}")
        return ""

    # Si no se extrajo texto y OCR esta disponible, usar OCR
    if not has_text and use_ocr_fallback:
        if OCR_AVAILABLE:
            print(f"  PDF escaneado detectado, usando OCR...")
            text = extract_text_with_ocr(file_path)
        else:
            print(f"  Advertencia: PDF escaneado pero OCR no disponible")
            print(f"  Instala: pip install pytesseract pdf2image")
            print(f"  Y asegurate de tener Tesseract OCR instalado")

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
