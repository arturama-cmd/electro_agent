"""
Procesador de archivos LaTeX para extraer contenido relevante.
Convierte archivos .tex a texto limpio para ser usado en RAG.
"""
import re
import os
from typing import List, Dict


def clean_latex(text: str) -> str:
    """
    Limpia comandos LaTeX y deja el contenido matematico legible.
    """
    # Eliminar comentarios
    text = re.sub(r'%.*', '', text)

    # Preservar ecuaciones importantes
    text = re.sub(r'\\begin\{equation\}(.*?)\\end\{equation\}', r'ECUACION: \1', text, flags=re.DOTALL)
    text = re.sub(r'\\begin\{align\*?\}(.*?)\\end\{align\*?\}', r'ECUACION: \1', text, flags=re.DOTALL)
    text = re.sub(r'\\begin\{eqnarray\}(.*?)\\end\{eqnarray\}', r'ECUACION: \1', text, flags=re.DOTALL)
    text = re.sub(r'\\\[(.*?)\\\]', r'ECUACION: \1', text, flags=re.DOTALL)
    text = re.sub(r'\$\$(.*?)\$\$', r'ECUACION: \1', text, flags=re.DOTALL)
    text = re.sub(r'\$(.*?)\$', r'MATH: \1', text)

    # Eliminar entornos de dibujo
    text = re.sub(r'\\begin\{circuitikz\}.*?\\end\{circuitikz\}', '[DIAGRAMA DE CIRCUITO]', text, flags=re.DOTALL)
    text = re.sub(r'\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}', '[DIAGRAMA]', text, flags=re.DOTALL)
    text = re.sub(r'\\includegraphics.*?\{.*?\}', '[IMAGEN]', text)

    # Eliminar comandos de formato
    text = re.sub(r'\\documentclass.*', '', text)
    text = re.sub(r'\\usepackage.*', '', text)
    text = re.sub(r'\\geometry.*', '', text)
    text = re.sub(r'\\begin\{document\}', '', text)
    text = re.sub(r'\\end\{document\}', '', text)
    text = re.sub(r'\\newpage', '\n---NUEVA PAGINA---\n', text)
    text = re.sub(r'\\clearpage', '\n---NUEVA PAGINA---\n', text)

    # Simplificar comandos de texto
    text = re.sub(r'\\textbf\{(.*?)\}', r'**\1**', text)
    text = re.sub(r'\\textit\{(.*?)\}', r'*\1*', text)
    text = re.sub(r'\\textcolor\{[^}]+\}\{(.*?)\}', r'\1', text)
    text = re.sub(r'\\section\*?\{(.*?)\}', r'\n## \1\n', text)
    text = re.sub(r'\\subsection\*?\{(.*?)\}', r'\n### \1\n', text)
    text = re.sub(r'\\paragraph\{(.*?)\}', r'\n**\1**\n', text)

    # Limpiar entornos de listas
    text = re.sub(r'\\begin\{enumerate\}.*?\{(.*?)\}', r'\nLISTA:', text)
    text = re.sub(r'\\begin\{enumerate\}', '\nLISTA:', text)
    text = re.sub(r'\\end\{enumerate\}', '', text)
    text = re.sub(r'\\begin\{itemize\}', '\nLISTA:', text)
    text = re.sub(r'\\end\{itemize\}', '', text)
    text = re.sub(r'\\item\[(.*?)\]', r'\n- \1: ', text)
    text = re.sub(r'\\item', '\n- ', text)

    # Limpiar otros entornos
    text = re.sub(r'\\begin\{minipage\}.*?\{.*?\}', '', text)
    text = re.sub(r'\\end\{minipage\}', '', text)
    text = re.sub(r'\\begin\{center\}', '', text)
    text = re.sub(r'\\end\{center\}', '', text)
    text = re.sub(r'\\begin\{wrapfigure\}.*?\{.*?\}', '', text)
    text = re.sub(r'\\end\{wrapfigure\}', '', text)

    # Eliminar comandos residuales
    text = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', text)
    text = re.sub(r'\\[a-zA-Z]+', '', text)

    # Limpiar espacios
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)

    return text.strip()


def extract_chunks_from_tex(file_path: str, category: str) -> List[Dict[str, str]]:
    """Extrae chunks de contenido de un archivo .tex."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='latin-1') as f:
            content = f.read()

    cleaned = clean_latex(content)
    chunks = []
    sections = re.split(r'---NUEVA PAGINA---|## Problema', cleaned)
    filename = os.path.basename(file_path)

    for i, section in enumerate(sections):
        if section.strip():
            chunks.append({
                "source": filename,
                "category": category,
                "chunk_number": str(i),
                "content": section.strip(),
                "file_type": "tex"
            })

    return chunks


def process_all_files_in_category(category_path: str, category_name: str) -> List[Dict]:
    """Procesa todos los archivos (.tex y .pdf) en una carpeta de categoria."""
    from pdf_processor import process_pdf_to_chunks

    all_chunks = []

    if not os.path.exists(category_path):
        print(f"  Carpeta no existe: {category_path}")
        return all_chunks

    for file in os.listdir(category_path):
        file_path = os.path.join(category_path, file)

        if os.path.isdir(file_path) or file.startswith('.'):
            continue

        try:
            if file.lower().endswith(".tex"):
                print(f"    Procesando LaTeX: {file}")
                chunks = extract_chunks_from_tex(file_path, category_name)
                all_chunks.extend(chunks)
            elif file.lower().endswith(".pdf"):
                print(f"    Procesando PDF: {file}")
                chunks = process_pdf_to_chunks(file_path, category_name)
                all_chunks.extend(chunks)
        except Exception as e:
            print(f"    Error procesando {file}: {e}")

    return all_chunks


def extract_problems_from_tex(file_path: str) -> List[Dict[str, str]]:
    """Funcion legacy para compatibilidad."""
    return extract_chunks_from_tex(file_path, "legacy")


def process_all_tex_files(directory: str = ".") -> List[Dict[str, str]]:
    """Funcion legacy para compatibilidad."""
    all_problems = []
    for file in os.listdir(directory):
        if file.endswith(".tex"):
            file_path = os.path.join(directory, file)
            problems = extract_chunks_from_tex(file_path, "legacy")
            all_problems.extend(problems)
    return all_problems
