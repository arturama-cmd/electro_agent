"""
Script de verificacion de entorno para ElectroAgent.
Ejecutar con: python check_environment.py

Este script verifica todas las dependencias necesarias para ejecutar
la aplicacion en un nuevo PC con Windows 11.
"""
import sys
import os
import subprocess
from pathlib import Path

# Colores ANSI para terminal
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"

def print_header(text):
    print(f"\n{BOLD}{BLUE}{'='*50}{RESET}")
    print(f"{BOLD}{BLUE}  {text}{RESET}")
    print(f"{BOLD}{BLUE}{'='*50}{RESET}\n")

def print_ok(text):
    print(f"  {GREEN}[OK]{RESET} {text}")

def print_error(text):
    print(f"  {RED}[ERROR]{RESET} {text}")

def print_warn(text):
    print(f"  {YELLOW}[WARN]{RESET} {text}")

def print_info(text):
    print(f"  {BLUE}[INFO]{RESET} {text}")

def check_python_version():
    """Verifica version de Python."""
    print(f"{BOLD}[1/8] Verificando Python...{RESET}")
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"

    if version.major >= 3 and version.minor >= 8:
        print_ok(f"Python {version_str}")
        return True
    else:
        print_error(f"Python {version_str} - Se requiere 3.8+")
        return False

def check_venv():
    """Verifica si estamos en un entorno virtual."""
    print(f"\n{BOLD}[2/8] Verificando entorno virtual...{RESET}")

    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    venv_path = Path("venv")

    if in_venv:
        print_ok(f"Entorno virtual activo: {sys.prefix}")
        return True
    elif venv_path.exists():
        print_warn("Entorno virtual existe pero NO esta activado")
        print_info("Ejecuta: venv\\Scripts\\activate")
        return False
    else:
        print_error("Entorno virtual no existe")
        print_info("Ejecuta: python -m venv venv")
        return False

def check_dependencies():
    """Verifica dependencias de requirements.txt."""
    print(f"\n{BOLD}[3/8] Verificando dependencias Python...{RESET}")

    required = {
        "streamlit": "streamlit",
        "anthropic": "anthropic",
        "chromadb": "chromadb",
        "python-dotenv": "dotenv",
        "pdfplumber": "pdfplumber",
        "pytesseract": "pytesseract",
        "pdf2image": "pdf2image",
        "pillow": "PIL",
        "numpy": "numpy"
    }

    missing = []
    installed = []

    for pkg_name, import_name in required.items():
        try:
            __import__(import_name)
            installed.append(pkg_name)
        except ImportError:
            missing.append(pkg_name)

    for pkg in installed:
        print_ok(pkg)

    for pkg in missing:
        print_error(f"{pkg} - no instalado")

    if missing:
        print_info("Ejecuta: pip install -r requirements.txt")
        return False
    return True

def check_tesseract():
    """Verifica instalacion de Tesseract OCR."""
    print(f"\n{BOLD}[4/8] Verificando Tesseract OCR...{RESET}")

    tesseract_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ]

    for path in tesseract_paths:
        if os.path.exists(path):
            print_ok(f"Tesseract encontrado: {path}")
            return True

    print_warn("Tesseract OCR no encontrado")
    print_info("PDFs escaneados no podran procesarse con OCR")
    print_info("Instalar desde: https://github.com/UB-Mannheim/tesseract/wiki")
    return False

def check_poppler():
    """Verifica instalacion de Poppler."""
    print(f"\n{BOLD}[5/8] Verificando Poppler (PDF tools)...{RESET}")

    project_dir = Path(__file__).parent
    poppler_path = project_dir / "poppler-24.08.0" / "Library" / "bin" / "pdftoppm.exe"

    if poppler_path.exists():
        print_ok(f"Poppler encontrado: {poppler_path.parent}")
        return True

    print_warn("Poppler no encontrado en el proyecto")
    print_info("Conversion PDF a imagen no disponible")
    return False

def check_env_file():
    """Verifica archivo .env con API key."""
    print(f"\n{BOLD}[6/8] Verificando configuracion (.env)...{RESET}")

    env_path = Path(".env")
    env_example = Path(".env.local.example")

    if not env_path.exists():
        print_error("Archivo .env no existe")
        if env_example.exists():
            print_info("Copia .env.local.example a .env y configura")
        else:
            print_info("Crea .env con: ANTHROPIC_API_KEY=tu-api-key")
        return False

    with open(env_path, 'r') as f:
        content = f.read()

    if "ANTHROPIC_API_KEY" in content and "sk-ant-" in content:
        print_ok("ANTHROPIC_API_KEY configurada")
        return True
    elif "LLM_BACKEND=ollama" in content:
        print_ok("Configurado para usar Ollama (modelo local)")
        return True
    else:
        print_warn("API key no configurada o incompleta")
        print_info("Edita .env y agrega tu ANTHROPIC_API_KEY")
        return False

def check_corpus():
    """Verifica que existe el corpus."""
    print(f"\n{BOLD}[7/8] Verificando corpus de documentos...{RESET}")

    corpus_path = Path("corpus")

    if not corpus_path.exists():
        print_error("Carpeta corpus/ no existe")
        return False

    categories = ["campo_electrico", "campo_magnetico"]
    found_files = 0

    for cat in categories:
        cat_path = corpus_path / cat
        if cat_path.exists():
            files = list(cat_path.glob("*.tex")) + list(cat_path.glob("*.pdf"))
            found_files += len(files)
            if files:
                print_ok(f"{cat}: {len(files)} archivos")
            else:
                print_warn(f"{cat}: vacio")

    if found_files == 0:
        print_warn("Corpus vacio - agrega archivos .tex o .pdf")
        return False

    return True

def check_chromadb():
    """Verifica estado de ChromaDB."""
    print(f"\n{BOLD}[8/8] Verificando ChromaDB...{RESET}")

    chroma_path = Path("chroma_db")

    if chroma_path.exists():
        print_ok("Base de datos ChromaDB existe")
        print_info("Si hay problemas, elimina chroma_db/ y reindexa")
        return True
    else:
        print_info("ChromaDB se creara automaticamente al iniciar")
        return True

def main():
    print_header("ElectroAgent - Verificacion de Entorno")
    print(f"  Directorio: {os.getcwd()}")
    print(f"  Python: {sys.executable}")

    results = {
        "Python": check_python_version(),
        "Entorno Virtual": check_venv(),
        "Dependencias": check_dependencies(),
        "Tesseract OCR": check_tesseract(),
        "Poppler": check_poppler(),
        "Configuracion": check_env_file(),
        "Corpus": check_corpus(),
        "ChromaDB": check_chromadb(),
    }

    print_header("Resumen")

    critical_ok = all([
        results["Python"],
        results["Dependencias"],
        results["Configuracion"],
    ])

    for name, status in results.items():
        if status:
            print_ok(name)
        else:
            if name in ["Tesseract OCR", "Poppler"]:
                print_warn(f"{name} (opcional)")
            else:
                print_error(name)

    print()
    if critical_ok:
        print(f"{GREEN}{BOLD}Sistema listo para ejecutar ElectroAgent{RESET}")
        print(f"\nComando para iniciar:")
        print(f"  {BLUE}streamlit run app.py{RESET}")
        return 0
    else:
        print(f"{RED}{BOLD}Hay problemas que resolver antes de iniciar{RESET}")
        print(f"\nRevisa los errores arriba y corrigelos.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
