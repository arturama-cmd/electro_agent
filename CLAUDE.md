# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**electro_agent** is a RAG-based conversational AI assistant for electromagnetics education at Universidad del Bio-Bio. It uses `claude-sonnet-4-6`, Streamlit, and ChromaDB to answer engineering students' questions using retrieved context from solved problems (LaTeX/PDF). UI and corpus content are in Spanish.

## Commands

```bash
# Setup (Windows)
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Verify all dependencies are correctly installed
python check_environment.py

# Run the application
streamlit run app.py

# Add a single PDF to existing ChromaDB
# Edit add_single_pdf.py lines 74-75 to set pdf_path and category, then run:
python add_single_pdf.py

# Test PDF processor (outputs chunk count and preview)
python pdf_processor.py "path/to/file.pdf"

# Compile a LaTeX solution (from project root) — works for any Solucion_*.tex
pdflatex -interaction=nonstopmode -output-directory=corpus/campo_electrico corpus/campo_electrico/Solucion_vec1.tex
# Pattern: replace the filename; output dir must match the source dir

# Force reindex: delete chroma_db/ folder and restart app
# Or use UI "Reindexar todo el corpus" button in Upload tab -> Advanced options
```

## Architecture

```
User Query -> app.py (Streamlit UI)
                 |
          rag_system.py (ElectromagnetismRAG)
                 |
     +-----------+-----------+
     |                       |
 ChromaDB               Claude API
 (vector search)        (response generation)
     ^
 tex_processor.py <-- corpus/*.tex
 pdf_processor.py <-- corpus/*.pdf
```

### Core Modules

| File | Purpose |
|------|---------|
| `app.py` | Mobile-first Streamlit UI with 3 tabs: Chat, Resolver (step-by-step solver), Subir (upload) |
| `rag_system.py` | `ElectromagnetismRAG` class: ChromaDB + Claude API orchestration |
| `tex_processor.py` | `clean_latex()` preserves math, `extract_chunks_from_tex()` splits files |
| `pdf_processor.py` | pdfplumber extraction with Tesseract OCR fallback |
| `add_single_pdf.py` | Add PDFs to existing vector DB without full reindex |
| `rag_system_local.py` | Multi-backend RAG variant supporting Ollama/vLLM/OpenAI-compatible APIs (for university deployment without Anthropic API) |
| `check_environment.py` | Validates all system dependencies (Tesseract, Poppler, Python packages, API key) |

### Data Flow

1. **Indexing** (first run or reindex):
   - `rag_system.index_corpus()` iterates `corpus/` subfolders
   - `.tex` files -> `tex_processor.extract_chunks_from_tex()`
   - `.pdf` files -> `pdf_processor.process_pdf_to_chunks()`
   - All chunks stored in ChromaDB with metadata via `collection.add()`

2. **Query Processing**:
   - `retrieve_relevant_problems(query, category_filter)` -> top 3 chunks via `collection.query()`
   - Each retrieved doc truncated to 1500 chars before being passed to the model
   - Context + conversation history -> Claude API `messages.create()`
   - Response rendered in Streamlit chat bubbles

### Knowledge Base

Documents in `corpus/` by topic (categories defined in `rag_system.py:13-19` -> `CATEGORIES` dict):

| Category | Status | Content |
|----------|--------|---------|
| `campo_electrico/` | Active | Exams, solutions, Sears/Serway textbook chapters |
| `campo_magnetico/` | Active | Homework solutions, Biot-Savart problems |
| `corriente_directa/` | Planned | DC circuits (empty) |
| `corriente_alterna/` | Planned | AC circuits (empty) |
| `maquinas_electricas/` | Planned | Electric machines (empty) |

### ChromaDB

- Collection: `electromagnetism_corpus`
- Persistence: `chroma_db/` (auto-created)
- First run downloads embedding model (`all-MiniLM-L6-v2`, ~79 MB) — no custom embedding function
- Delete `chroma_db/` to force complete reindex

### Chunk Metadata Schema

```python
{
    "source": "filename.tex",
    "category": "campo_electrico",       # key used for WHERE filter
    "category_display": "Campo Electrico",
    "chunk_number": "0",
    "file_type": "tex" | "pdf" | "manual"
}
```

## Key Implementation Details

**Category Filtering**: `retrieve_relevant_problems()` at `rag_system.py:73` accepts `category_filter` for WHERE clause on ChromaDB. The filter value must be the dict key (e.g. `"campo_electrico"`), not the display name.

**Text Extraction Pipeline**:
- LaTeX: Regex-based cleanup preserving equations (marked as `ECUACION:`/`MATH:`) in `tex_processor.py:10-72`
- PDF: pdfplumber first, Tesseract OCR fallback for scanned docs in `pdf_processor.py:84-124`
- Encoding: UTF-8 with latin-1 fallback in `tex_processor.py:78-82`
- Chunking split points: `---NUEVA PAGINA---` and `## Problema` delimiters (`tex_processor.py:86`)
- PDF chunks split by page first, then by paragraph if page exceeds `chunk_size` (default 2000 chars)

**Corpus Indexing Limitation**: `process_all_files_in_category()` at `tex_processor.py:112-115` uses `os.listdir` (non-recursive) and skips subdirectories. Files in subfolders (e.g. `corpus/campo_electrico/prob resueltos pdf/`) will **not** be auto-indexed — use `add_single_pdf.py` instead.

**Caching**: `@st.cache_resource` on `initialize_rag()` at `app.py:514-523` prevents re-init per session. Auto-indexes corpus on first run if collection is empty.

## Customization

| What | Where |
|------|-------|
| Claude system prompt | `rag_system.py:101-113` -> `system_prompt` variable |
| Retrieved chunk count | `rag_system.py:73` -> `n_results` parameter (default: 3) |
| Context chars per doc | `rag_system.py:99` -> `[:1500]` slice |
| Max response tokens | `rag_system.py:124` -> `max_tokens` (default: 4096) |
| Model | `rag_system.py:123` -> `claude-sonnet-4-6` |
| Add new category | `rag_system.py:13-19` -> `CATEGORIES` dict + create folder in `corpus/` |
| Conversation history limit | `app.py:631` -> slicing `[-10:]` (last 10 messages) |
| Single PDF add paths | `add_single_pdf.py:74-75` -> `pdf_path` and `category` variables |
| Tesseract path (Windows) | `pdf_processor.py:25` |
| Poppler path (Windows) | `pdf_processor.py:38` |
| Local LLM backend | `rag_system_local.py` env vars: `LLM_BACKEND` (`anthropic`/`ollama`/`vllm`/`openai_compatible`), `LOCAL_MODEL_URL`, `LOCAL_MODEL_NAME` |

## System Dependencies

| Dependency | Purpose | Location |
|------------|---------|----------|
| Tesseract OCR | Scanned PDF extraction | `C:\Program Files\Tesseract-OCR` |
| Poppler | PDF to image conversion | `poppler-24.08.0/Library/bin/` (included) |
| tessdata | Spanish OCR models | `tessdata/` (included) |

## Solution Generator (LaTeX/PDF)

**Physics convention**: Coulomb's law in vector form must be written as **K·q·r_vec/r³** (not K·q·r̂/r²). These are mathematically equivalent but the r_vec/r³ form is required for consistency with the existing solutions.

Solutions in `corpus/*/Solucion_*.tex` follow this structure:
1. Problem statement with TikZ diagram (2D or 3D)
2. Numerical data (given values with SI units)
3. Qualitative analysis (force directions, charge interactions)
4. Step-by-step calculation with position vectors and unit application
5. Boxed final result (`\boxed{}`)
6. Physical interpretation

**TikZ libraries required:**
```latex
\usetikzlibrary{3d,calc,decorations.markings,patterns}
```

## Notes

- API key: `.env` file with `ANTHROPIC_API_KEY`
- Session logs: `.claude/logs/YYYY-MM-DD_session_log.md`
- Textbook PDFs (Sears, Serway) are gitignored due to copyright
- Git remote must include the username to avoid 403 auth errors:
  ```bash
  git remote set-url origin https://arturama-cmd@github.com/arturama-cmd/electro_agent.git
  ```
