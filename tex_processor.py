"""
Procesador de archivos LaTeX para extraer contenido relevante.
Convierte archivos .tex a texto limpio para ser usado en RAG.
"""
import re
import os
from typing import List, Dict


def clean_latex(text: str) -> str:
    """
    Limpia comandos LaTeX y deja el contenido matemático legible.
    """
    # Eliminar comentarios
    text = re.sub(r'%.*', '', text)

    # Preservar ecuaciones importantes (convertir a formato más legible)
    text = re.sub(r'\\begin\{equation\}(.*?)\\end\{equation\}', r'ECUACION: \1', text, flags=re.DOTALL)
    text = re.sub(r'\\begin\{align\*?\}(.*?)\\end\{align\*?\}', r'ECUACION: \1', text, flags=re.DOTALL)
    text = re.sub(r'\\begin\{eqnarray\}(.*?)\\end\{eqnarray\}', r'ECUACION: \1', text, flags=re.DOTALL)
    text = re.sub(r'\\\[(.*?)\\\]', r'ECUACION: \1', text, flags=re.DOTALL)
    text = re.sub(r'\$\$(.*?)\$\$', r'ECUACION: \1', text, flags=re.DOTALL)
    text = re.sub(r'\$(.*?)\$', r'MATH: \1', text)

    # Eliminar entornos de dibujo (circuitikz, tikzpicture, etc.)
    text = re.sub(r'\\begin\{circuitikz\}.*?\\end\{circuitikz\}', '[DIAGRAMA DE CIRCUITO]', text, flags=re.DOTALL)
    text = re.sub(r'\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}', '[DIAGRAMA]', text, flags=re.DOTALL)
    text = re.sub(r'\\includegraphics.*?\{.*?\}', '[IMAGEN]', text)

    # Eliminar comandos de formato comunes
    text = re.sub(r'\\documentclass.*', '', text)
    text = re.sub(r'\\usepackage.*', '', text)
    text = re.sub(r'\\geometry.*', '', text)
    text = re.sub(r'\\begin\{document\}', '', text)
    text = re.sub(r'\\end\{document\}', '', text)
    text = re.sub(r'\\newpage', '\n---NUEVA PÁGINA---\n', text)
    text = re.sub(r'\\clearpage', '\n---NUEVA PÁGINA---\n', text)

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

    # Limpiar otros entornos comunes
    text = re.sub(r'\\begin\{minipage\}.*?\{.*?\}', '', text)
    text = re.sub(r'\\end\{minipage\}', '', text)
    text = re.sub(r'\\begin\{center\}', '', text)
    text = re.sub(r'\\end\{center\}', '', text)
    text = re.sub(r'\\begin\{wrapfigure\}.*?\{.*?\}', '', text)
    text = re.sub(r'\\end\{wrapfigure\}', '', text)

    # Eliminar comandos residuales
    text = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', text)
    text = re.sub(r'\\[a-zA-Z]+', '', text)

    # Limpiar espacios múltiples y líneas vacías excesivas
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)

    return text.strip()


def extract_problems_from_tex(file_path: str) -> List[Dict[str, str]]:
    """
    Extrae problemas individuales de un archivo .tex.
    Retorna una lista de diccionarios con metadata de cada problema.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Limpiar el contenido
    cleaned = clean_latex(content)

    # Identificar problemas (pueden estar marcados con \item[1.], \item[2.], etc.)
    # O por secciones con "Problema"
    problems = []

    # Dividir por "---NUEVA PÁGINA---" o por marcadores de problema
    sections = re.split(r'---NUEVA PÁGINA---|## Problema', cleaned)

    filename = os.path.basename(file_path)

    for i, section in enumerate(sections):
        if section.strip():
            # Intentar identificar el tipo de problema
            problem_type = "Desconocido"
            if "capacitor" in section.lower() or "capacitancia" in section.lower():
                problem_type = "Capacitores"
            elif "resistencia" in section.lower() or "kirchhoff" in section.lower():
                problem_type = "Circuitos y Leyes de Kirchhoff"
            elif "campo eléctrico" in section.lower() or "campo el" in section.lower():
                problem_type = "Campos Eléctricos"
            elif "carga" in section.lower() and "campo" in section.lower():
                problem_type = "Cargas y Campos Eléctricos"

            problems.append({
                "source": filename,
                "problem_number": i,
                "type": problem_type,
                "content": section.strip()
            })

    return problems


def process_all_tex_files(directory: str = ".") -> List[Dict[str, str]]:
    """
    Procesa todos los archivos .tex en un directorio.
    """
    all_problems = []

    for file in os.listdir(directory):
        if file.endswith(".tex"):
            file_path = os.path.join(directory, file)
            problems = extract_problems_from_tex(file_path)
            all_problems.extend(problems)

    return all_problems


if __name__ == "__main__":
    # Test del procesador
    problems = process_all_tex_files("/home/dell/Escritorio/electro_agent")
    print(f"Se encontraron {len(problems)} problemas")
    for i, prob in enumerate(problems[:2]):
        print(f"\n{'='*50}")
        print(f"Problema {i+1} - Tipo: {prob['type']}")
        print(f"Fuente: {prob['source']}")
        print(f"Contenido (primeros 300 caracteres):\n{prob['content'][:300]}")
