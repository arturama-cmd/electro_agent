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

# Add a single PDF to existing ChromaDB
python add_single_pdf.py

# Test PDF processor
python pdf_processor.py "path/to/file.pdf"

# Compile LaTeX solutions
cd corpus/campo_electrico && pdflatex -interaction=nonstopmode "Solucion_Tema_I.tex"
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
```

### Key Files

| File | Purpose |
|------|---------|
| `app.py` | Streamlit UI entry point, session management, `@st.cache_resource` for lazy RAG init |
| `rag_system.py` | RAG orchestrator: `ElectromagnetismRAG` class with ChromaDB integration and Claude API calls |
| `tex_processor.py` | LaTeX parsing: `clean_latex()` preserves math while removing markup, `extract_chunks_from_tex()` splits files |
| `pdf_processor.py` | PDF extraction with OCR fallback via pytesseract |
| `add_single_pdf.py` | Utility to add PDFs to existing vector database |

### Knowledge Base

Documents are organized by topic in `corpus/`:
- `campo_electrico/` - Electric field problems (active)
- `campo_magnetico/` - Magnetic field (planned)
- `corriente_directa/` - DC circuits (planned)
- `corriente_alterna/` - AC circuits (planned)
- `maquinas_electricas/` - Electric machines (planned)

Categories are defined in `rag_system.py` → `CATEGORIES` dict.

### ChromaDB

- Auto-generated in `chroma_db/` on first run
- Downloads embedding model (~79 MB) on first initialization
- Delete `chroma_db/` folder to force complete reindex
- Use sidebar "Reindexar Corpus" button for reindex from UI

## Key Patterns

**Category Filtering**: RAG retrieval uses `where_filter` in `retrieve_relevant_problems()` to limit search to specific topics.

**Metadata-Rich Chunks**: Each chunk includes `source`, `category`, `category_display`, `chunk_number`, `file_type`.

**Fallback Text Extraction**: PDFs try direct extraction via pdfplumber first, then OCR if content is scanned.

## Customization Points

- **Claude behavior**: Edit `system_prompt` in `rag_system.py` → `generate_response()`
- **Retrieval count**: Modify `n_results` parameter in `generate_response()` (default: 3)
- **Model**: Currently uses `claude-sonnet-4-20250514`

## System Dependencies

- Tesseract OCR for scanned PDFs (Windows: `C:\Program Files\Tesseract-OCR`)
- Poppler included locally in `poppler-24.08.0/Library/bin/`
- tessdata directory for OCR language models (includes Spanish)

## Development Notes

- Primary language: Spanish (UI and corpus content)
- API key configured via `.env` file (`ANTHROPIC_API_KEY`)

## Solution Generator (LaTeX/PDF)

Generates detailed solutions for electromagnetics problems with TikZ diagrams.

### Solution Format

Solutions in `corpus/campo_electrico/Solucion_*.tex` follow this structure:
- Problem statement with TikZ diagram (2D or 3D)
- Qualitative analysis (attractive/repulsive forces)
- Detailed calculation with position vectors
- Boxed final result
- Physical interpretation

### TikZ Libraries Required

```latex
\usetikzlibrary{3d,calc,decorations.markings,patterns}
```

## Session Logs

Session logs are stored in `.claude/logs/` with format `YYYY-MM-DD_session_log.md`.
