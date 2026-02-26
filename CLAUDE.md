# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**electro_agent** is a RAG-based conversational AI assistant for electromagnetics education. It uses Claude Sonnet 4, Streamlit, and ChromaDB to answer engineering students' questions using retrieved context from solved problems (LaTeX/PDF).

## Commands

```bash
# Setup
pip install -r requirements.txt

# Run the application
streamlit run app.py

# Add a single PDF to existing ChromaDB (edit file to set path/category)
python add_single_pdf.py

# Test PDF processor (outputs chunk count and preview)
python pdf_processor.py "path/to/file.pdf"

# Compile LaTeX solutions
cd corpus/campo_electrico && pdflatex -interaction=nonstopmode "Solucion_Tema_I.tex"

# Force reindex: delete chroma_db/ folder and restart app
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
| `app.py` | Streamlit UI, session state, `@st.cache_resource` for lazy RAG init |
| `rag_system.py` | `ElectromagnetismRAG` class: ChromaDB + Claude API orchestration |
| `tex_processor.py` | `clean_latex()` preserves math, `extract_chunks_from_tex()` splits files |
| `pdf_processor.py` | pdfplumber extraction with Tesseract OCR fallback |
| `add_single_pdf.py` | Add PDFs to existing vector DB without full reindex |

### Data Flow

1. **Indexing** (first run or reindex):
   - `rag_system.index_corpus()` iterates `corpus/` subfolders
   - `.tex` files → `tex_processor.extract_chunks_from_tex()`
   - `.pdf` files → `pdf_processor.process_pdf_to_chunks()`
   - All chunks stored in ChromaDB with metadata

2. **Query Processing**:
   - `retrieve_relevant_problems(query, category_filter)` → top 3 chunks
   - Context + conversation history → Claude API
   - Streaming response rendered in Streamlit

### Knowledge Base

Documents in `corpus/` by topic (categories defined in `rag_system.py` → `CATEGORIES` dict):

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
- UI reindex: sidebar "Reindexar Corpus" button

### Chunk Metadata Schema

```python
{
    "source": "filename.tex",
    "category": "campo_electrico",
    "category_display": "Campo Eléctrico",
    "chunk_number": "0",
    "file_type": "tex" | "pdf"
}
```

## Key Implementation Details

**Category Filtering**: `retrieve_relevant_problems()` accepts `category_filter` for WHERE clause on ChromaDB.

**Text Extraction Pipeline**:
- LaTeX: Regex-based cleanup preserving equations (marks as `ECUACION:`/`MATH:`)
- PDF: pdfplumber first, Tesseract OCR fallback for scanned docs
- Encoding: UTF-8 with latin-1 fallback

**Caching**: `@st.cache_resource` on `initialize_rag()` prevents re-init per session.

## Customization

| What | Where |
|------|-------|
| Claude system prompt | `rag_system.py` → `generate_response()` → `system_prompt` |
| Retrieved chunk count | `generate_response()` → `n_results` (default: 3) |
| Model | `rag_system.py` → `claude-sonnet-4-20250514` |
| Add new category | `rag_system.py` → `CATEGORIES` dict + create folder in `corpus/` |

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
