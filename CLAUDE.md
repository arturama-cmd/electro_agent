# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**electro_agent** is a RAG-based conversational AI assistant for electromagnetics education. It uses Claude Sonnet 4, Streamlit, and ChromaDB to answer engineering students' questions using retrieved context from solved problems (LaTeX/PDF).

## Commands

```bash
# Setup (Windows)
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Run the application
streamlit run app.py

# Add a single PDF to existing ChromaDB
# Edit add_single_pdf.py lines 74-75 to set pdf_path and category, then run:
python add_single_pdf.py

# Test PDF processor (outputs chunk count and preview)
python pdf_processor.py "path/to/file.pdf"

# Compile LaTeX solutions (from project root)
pdflatex -interaction=nonstopmode -output-directory=corpus/campo_electrico corpus/campo_electrico/Solucion_Tema_I.tex

# Force reindex: delete chroma_db/ folder and restart app
# Or use UI "Reindexar todo el corpus" button in Upload tab → Advanced options
```

## Architecture

```
User Query → app.py (Streamlit UI)
                ↓
         rag_system.py (ElectromagnetismRAG)
                ↓
    ┌───────────┴───────────┐
    ↓                       ↓
ChromaDB               Claude API
(vector search)        (response generation)
    ↑
tex_processor.py ←── corpus/*.tex
pdf_processor.py ←── corpus/*.pdf
```

### Core Modules

| File | Purpose |
|------|---------|
| `app.py` | Mobile-first Streamlit UI with 3 tabs (Chat, Solver, Upload) |
| `rag_system.py` | `ElectromagnetismRAG` class: ChromaDB + Claude API orchestration |
| `tex_processor.py` | `clean_latex()` preserves math, `extract_chunks_from_tex()` splits files |
| `pdf_processor.py` | pdfplumber extraction with Tesseract OCR fallback |
| `add_single_pdf.py` | Add PDFs to existing vector DB without full reindex |

### Data Flow

1. **Indexing** (first run or reindex):
   - `rag_system.index_corpus()` iterates `corpus/` subfolders
   - `.tex` files → `tex_processor.extract_chunks_from_tex()`
   - `.pdf` files → `pdf_processor.process_pdf_to_chunks()`
   - All chunks stored in ChromaDB with metadata via `collection.add()`

2. **Query Processing**:
   - `retrieve_relevant_problems(query, category_filter)` → top 3 chunks via `collection.query()`
   - Context + conversation history → Claude API `messages.create()`
   - Response rendered in Streamlit chat bubbles

### Knowledge Base

Documents in `corpus/` by topic (categories defined in `rag_system.py:13-19` → `CATEGORIES` dict):

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
- First run downloads embedding model (~79 MB)
- Delete folder to force complete reindex
- UI reindex: Upload tab → Advanced options → "Reindexar todo el corpus"

### Chunk Metadata Schema

```python
{
    "source": "filename.tex",
    "category": "campo_electrico",
    "category_display": "Campo Eléctrico",
    "chunk_number": "0",
    "file_type": "tex" | "pdf" | "manual"
}
```

## Key Implementation Details

**Category Filtering**: `retrieve_relevant_problems()` at `rag_system.py:73` accepts `category_filter` for WHERE clause on ChromaDB.

**Text Extraction Pipeline**:
- LaTeX: Regex-based cleanup preserving equations (marks as `ECUACION:`/`MATH:`) in `tex_processor.py:10-72`
- PDF: pdfplumber first, Tesseract OCR fallback for scanned docs in `pdf_processor.py:84-124`
- Encoding: UTF-8 with latin-1 fallback in `tex_processor.py:78-82`

**Caching**: `@st.cache_resource` on `initialize_rag()` at `app.py:514-523` prevents re-init per session.

## Customization

| What | Where |
|------|-------|
| Claude system prompt | `rag_system.py:101-113` → `system_prompt` variable |
| Retrieved chunk count | `rag_system.py:73` → `n_results` parameter (default: 3) |
| Max response tokens | `rag_system.py:124` → `max_tokens` (default: 4096) |
| Model | `rag_system.py:123` → `claude-sonnet-4-20250514` |
| Add new category | `rag_system.py:13-19` → `CATEGORIES` dict + create folder in `corpus/` |
| Conversation history limit | `app.py:631` → slicing `[-10:]` (last 10 messages) |
| Single PDF add paths | `add_single_pdf.py:74-75` → `pdf_path` and `category` variables |
| Tesseract path (Windows) | `pdf_processor.py:25` |
| Poppler path (Windows) | `pdf_processor.py:38` |

## System Dependencies

| Dependency | Purpose | Location |
|------------|---------|----------|
| Tesseract OCR | Scanned PDF extraction | `C:\Program Files\Tesseract-OCR` |
| Poppler | PDF to image conversion | `poppler-24.08.0/Library/bin/` (included) |
| tessdata | Spanish OCR models | `tessdata/` (included) |

## Solution Generator (LaTeX/PDF)

Solutions in `corpus/*/Solucion_*.tex` follow this structure:
1. Problem statement with TikZ diagram (2D or 3D)
2. Qualitative analysis (force directions, charge interactions)
3. Step-by-step calculation with position vectors
4. Boxed final result (`\boxed{}`)
5. Physical interpretation

**TikZ libraries required:**
```latex
\usetikzlibrary{3d,calc,decorations.markings,patterns}
```

## Notes

- UI and corpus content are in Spanish
- API key: `.env` file with `ANTHROPIC_API_KEY`
- Session logs: `.claude/logs/YYYY-MM-DD_session_log.md`
- Textbook PDFs (Sears, Serway) are gitignored due to copyright
- First run downloads sentence-transformers embedding model (~79 MB) - be patient
- ChromaDB uses default `all-MiniLM-L6-v2` embeddings (no custom embedding function)
- UI has 3 main tabs: Chat (conversation), Resolver (step-by-step solver), Subir (upload to corpus)
