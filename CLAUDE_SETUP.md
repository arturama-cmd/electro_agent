# CLAUDE_SETUP.md

Instrucciones para Claude Code al iniciar en un nuevo PC Windows 11.

## Accion Inmediata al Iniciar

Cuando el usuario inicie sesion en un nuevo PC, ejecuta este script de verificacion:

```bash
python check_environment.py
```

Este script verifica automaticamente todas las dependencias y muestra un resumen del estado.

## Punto de Restauracion

Este proyecto es **electro_agent**, un asistente RAG de electromagnetismo para estudiantes de ingenieria. Usa Claude Sonnet 4 + ChromaDB + Streamlit.

## Verificacion Manual (si el script falla)

### 1. Verificar Python
```bash
python --version
```
Requiere: Python 3.8+

### 2. Verificar/Crear entorno virtual
```bash
# Si no existe venv/
python -m venv venv

# Activar (Windows)
venv\Scripts\activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Verificar Tesseract OCR (opcional)
```bash
dir "C:\Program Files\Tesseract-OCR\tesseract.exe"
```
Solo necesario para PDFs escaneados. Instalar desde:
https://github.com/UB-Mannheim/tesseract/wiki

### 5. Configurar .env
```bash
# Ver si existe
type .env

# Si no existe, copiar plantilla
copy .env.local.example .env
```

**Dos modos de operacion:**

| Modo | Configuracion en .env |
|------|----------------------|
| API Anthropic | `ANTHROPIC_API_KEY=sk-ant-...` |
| Modelo Local (Ollama) | `LLM_BACKEND=ollama` + `LOCAL_MODEL_URL=http://localhost:11434` |

### 6. Iniciar aplicacion
```bash
streamlit run app.py
```

## Scripts Disponibles

| Script | Proposito |
|--------|-----------|
| `check_environment.py` | Verificacion completa del entorno |
| `setup_and_run.bat` | Setup automatico + iniciar app |

## Estructura Esperada

```
electro_agent/
├── app.py                  # UI Streamlit
├── rag_system.py           # RAG + Claude API
├── tex_processor.py        # Procesador LaTeX
├── pdf_processor.py        # Procesador PDF + OCR
├── check_environment.py    # Verificador de entorno
├── setup_and_run.bat       # Script inicio Windows
├── requirements.txt        # Dependencias Python
├── .env                    # REQUERIDO - configuracion
├── .env.local.example      # Plantilla configuracion
├── corpus/                 # Base de conocimiento
│   ├── campo_electrico/    # Problemas campo E
│   └── campo_magnetico/    # Problemas campo B
├── venv/                   # Entorno virtual Python
├── chroma_db/              # Vector DB (auto-generado)
├── tessdata/               # Modelos OCR espanol
└── poppler-24.08.0/        # PDF tools Windows
```

## Problemas Comunes

| Problema | Solucion |
|----------|----------|
| `ANTHROPIC_API_KEY no encontrada` | Crear/editar archivo `.env` con la API key |
| `No module named 'streamlit'` | `pip install -r requirements.txt` |
| `ChromaDB error` | Eliminar `chroma_db/` y reiniciar |
| Primera ejecucion lenta | Normal: descarga embeddings ~79MB |
| `venv\Scripts\activate` no funciona | Ejecutar: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |

## Comando Rapido de Inicio

```bash
cd C:\Users\Usuario\electro_agent && venv\Scripts\activate && streamlit run app.py
```

## Flujo de Trabajo Recomendado

1. Ejecutar `python check_environment.py`
2. Corregir cualquier error reportado
3. Ejecutar `streamlit run app.py`
4. Acceder a http://localhost:8501 en el navegador
