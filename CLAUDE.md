# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**electro_agent** is a RAG-based conversational AI assistant for electromagnetics education at Universidad del Bio-Bio. It uses `claude-sonnet-4-6`, Streamlit, and ChromaDB to answer engineering students' questions using retrieved context from solved problems (LaTeX/PDF). UI and corpus content are in Spanish.

## Commands

```bash
# Setup (Windows) — venv lives at ~/venv, NOT inside the project directory
python -m venv ~/venv
~/venv/Scripts/activate      # Windows
source ~/venv/bin/activate   # Linux/Mac (or use run.sh which does this automatically)
pip install -r requirements.txt

# Verify all dependencies are correctly installed
python check_environment.py

# Run the application (two equivalent ways)
streamlit run app.py
./run.sh                     # Unix shortcut — activates venv + starts Streamlit

# Add a single PDF to existing ChromaDB
# Edit add_single_pdf.py lines 70-71 to set pdf_path and category, then run:
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
| `app.py` | Mobile-first Streamlit UI with 3 tabs: Chat, Resolver (RAG-backed step-by-step solver with structured 6-step prompt), Subir (upload) |
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
| `campo_magnetico/` | Active | Biot-Savart, fuerza/torque magnético, inducción electromagnética (Faraday/Lenz); soluciones de guías 8/9/10, certámenes (C3, C4) y tareas |
| `corriente_directa/` | Active | Capacitors, dielectrics, DC circuits (Guía 7 + class solutions + Certamen 2 Kirchhoff + Tarea 3 + Problema 12 Kirchhoff) |
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

**Corpus Indexing Limitation**: `process_all_files_in_category()` at `tex_processor.py:112-115` uses `os.listdir` (non-recursive) and skips subdirectories. Files in subfolders (e.g. `corpus/campo_electrico/prob resueltos pdf/`, `corpus/campo_electrico/gauss_imgs/`) will **not** be auto-indexed — use `add_single_pdf.py` instead. The `gauss_imgs/` folder holds image assets referenced by Gauss-law solutions via `\includegraphics`; they don't need indexing but must remain alongside the `.tex` files for compilation. `.docx` files are also not supported by any indexing pipeline — convert to PDF first if content needs to be searchable.

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
For solutions that draw Gaussian surfaces (sphere/shell cross-sections), also add `arrows.meta`:
```latex
\usetikzlibrary{calc,arrows.meta,decorations.markings,patterns}
```

**Gauss law solution template** (reference files by geometry):
- Planar: `Solucion_Gauss_plano.tex`
- Cylindrical (infinite wire): `Solucion_Gauss_hilo.tex`
- Cylindrical (coaxial cable, multi-region): `Solucion_Gauss_coaxial.tex`
- Spherical (conducting shell): `Solucion_Gauss_esf_v1.tex` / `Solucion_Gauss_esf_v2.tex`
- Spherical (insulating solid): `Solucion_Gauss_esf_aislante.tex`
- Spherical (conducting solid): `Solucion_Gauss_esf_conductora.tex`
- Spherical (non-concentric shell): `Solucion_Gauss_cascaron_nc.tex`

Shared conventions across all Gauss law templates:
- TikZ diagram: Gaussian surface drawn in red dotted line (`dashed, red`)
- Layout: `\begin{minipage}{0.30\textwidth}` (diagram) + `\begin{minipage}{0.67\textwidth}` (steps)
- Always define charge density before first use: `σ ≡ dq/dA`, `λ ≡ dq/dℓ`, `ρ ≡ dq/dV`
- 5 steps: define surface → write Gauss law → simplify flux → solve E → evaluate numerically
- End with a comparative table of all 3 classic cases (sphere/wire/plane: 1/r², 1/r, const)

**Potential electric solution templates** (reference files by problem type):
- Point charges (discrete): `Solucion_pot_elec_carg_punt.tex`
- Continuous charge distribution (1D — line charge + ring): `Solucion_pot_elec_1D_cont.tex`

**Solution file naming conventions** (use descriptive names, no strict rule, but these patterns are in use):
- `Solucion_vec[N].tex` — vector exercises (e.g. `Solucion_vec1.tex`)
- `Solucion_G[N]P[N][uni|bid].tex` — guide N, problem N (`uni`=unidimensional, `bid`=bidimensional)
- `Solucion_G[N]_P[list].tex` — guide N, multiple problems in one file
- `Solucion_C1P[N]_[year]-[semester].tex` — certamen problem breakdown (e.g. `Solucion_C1P1_2024-1.tex`)
- `Solucion_Guia[N].tex` — full guide solution (e.g. `Solucion_Guia1.tex`)
- `Solucion_Certamen[N]_[year].tex` — full certamen solution (e.g. `Solucion_Certamen1_2023.tex`, `Solucion_Certamen2_2020.tex`)
- `Solucion_C[N]_[year]-[semester].tex` — full certamen N solution, e.g. `Solucion_C2_2026-1.tex`
- `Solucion_C[N]_[year]-[semester]_Rec.tex` — certamen N recuperativo, e.g. `Solucion_C2_2026-1_Rec.tex`
- `Solucion_Certamen[N]_[year]_Rec.tex` — certamen recovery/retake solution (older naming)
- `Solucion_[topic].tex` — topic-specific (e.g. `Solucion_dipolo_HCl.tex`, `Solucion_clase_20-03.tex`)
- `Solucion_DDMM.tex` — date-based shorthand (e.g. `Solucion_2703.tex` = class on March 27)
- `Solucion_Tarea[N]_[year]-[semester].tex` — homework solution (e.g. `Solucion_Tarea1_2026-1.tex`)
- `Solucion_[topic]_esf_v[N].tex` — topic + geometry variant (e.g. `Solucion_Gauss_esf_v1.tex` = Gauss law, spherical geometry, version 1)

**Other corpus files** (also indexed alongside solutions): `guia[N].tex` and `guia_tarea[N]_[year]-[semester].tex` contain problem statements. Individual problem PDFs follow the pattern `prob [N] guia [N].pdf`. Student-facing exercise sheets (for printing/distribution) use `Prob_[N][Variant]_ejercicio.tex` (e.g. `Prob_2A_ejercicio.tex`, `Prob_2B_ejercicio.tex`) — these are enunciado-only files with UBB institutional header/footer (logos, fancyhdr), not solutions.

**DC circuit (Kirchhoff) solution template** (`corriente_directa/`):

Reference files: `Solucion_C2_2026-1.tex` (normal) and `Solucion_C2_2026-1_Rec.tex` (recuperativo).

Shared circuit topology for Certamen 2 problems: 2 nodes (a, b), 3 branches, 2 independent meshes.
- Branch top (I₁ ←): b → R₄ (right-upper rail) → TR → R₁ + ε₁ (top) → TL → [R₂ or wire] → a
- Branch mid (I₂ →): a → ε₂ + R₅ → b
- Branch bot (I₃ →): a → [wire or R₂] + ε₃ + R₃ → b

**Critical topology difference between Normal and Recuperativo:**
- Normal: R₂ on **upper-left** rail (TL→a) → I₁ coefficient = R₄+R₁+R₂; bottom path has only R₃.
- Recuperativo: R₂ on **lower-left** rail (a→BL) → I₁ coefficient = R₄+R₁; I₃ path has R₂+R₃.
Always deduce R₂ position from the mesh equations (coefficient of I₁ vs I₃) before drawing TikZ.

**TikZ DC circuit conventions** (established 2026-05-28):
- Resistors: colored filled rectangles (`\fill[color!25] ... \draw[color,thick] ...`)
  Color palette: R₁=red, R₂=blue, R₃=green, R₄=orange, R₅=violet
- Sources: standard 2-line battery symbol — long thin line = +, short thick line = −
  Color palette: ε₁=amber, ε₂=cyan-dark, ε₃=magenta; mark + terminal explicitly
- Wires: always black (`\draw[black]`)
- Node dots: `\fill[black] (x,y) circle (3.5pt)` with letter label beside
- Current arrows: placed outside the circuit frame with `\draw[->,black,thick]`
- LaTeX engine: **modern MiKTeX is installed** (since 2026-06-13, replacing the EOL MiKTeX 2.9). `arrows.meta`, `>=Stealth` and `circuitikz` all work now. The shell PATH may still point at the removed 2.9 — call pdflatex by full path: `C:/Users/Usuario/AppData/Local/Programs/MiKTeX/miktex/bin/x64/pdflatex.exe` (auto-installs missing packages; run twice for `\pageref{LastPage}`). Older hand-drawn files used `arrows`/`>=stealth` for 2.9 compat — leave them as-is.
- Minipage layout for part a): 38% width for small circuit diagram + mesh arrows, 58% for KVL/KCL equations

**Battery polarity rules** (verified against pauta):
- ε drives current in the direction labeled by its current arrow → + terminal faces the current's source node.
- ε₁ (top branch, I₁ goes TR→TL): + at TL side
- ε₂ (middle branch, I₂ goes a→b): + at a side  
- ε₃ (bottom branch, I₃ goes BL→BR): + at BR side

**circuitikz for circuit diagrams** (preferred since 2026-06-13, after the MiKTeX upgrade — `Solucion_tarea3_P1/P2/P3`): use circuitikz instead of hand-drawn TikZ rectangles for new circuit figures (cleaner, matches the professor's reference figures).
- Preamble: `\usepackage[american]{circuitikz}` after `\usepackage{tikz}`; mesh-loop arrows need `\usetikzlibrary{decorations.markings}`.
- Components: `to[battery1,l=...]` (DC source), `to[R,l=...]` (resistor, zigzag), `to[C,l=...]` (capacitor), `to[short,i>^={$I_1$}]` (wire carrying a labeled current).
- **`battery1` polarity**: the long bar (+ terminal) sits at the FIRST coordinate of the `to[battery1]` path. Use the `invert` option to flip it. (e.g. `(0,2) to[battery1] (0,0)` → + at top; verified empirically.)
- **Label math-mode gotcha**: circuitikz labels are typeset in TEXT mode — wrap `\mathrm`/`\,` in `$...$` (e.g. `l_=$10\,\mathrm{V}$`, not `l_=10\,\mathrm{V}`, which throws "\mathrm allowed only in math mode" and halts a normal compile). `l=$3\,\Omega$` is fine.
- **Mesh loops** (M₁, M₂): blue dashed arc + arrowhead (professor's style):
  ```latex
  \draw[blue,dashed,very thick,postaction={decorate},
        decoration={markings, mark=at position 1 with {\arrow[blue,scale=1.2]{>}}}]
    (Mx)+(90:\rA) arc[start angle=90, end angle=360, radius=\rA];
  \node[blue] at (Mx) {$M_1$};
  ```
- Node dots: `\node[circ] at (x,y){};`. The professor's circuitikz reference is `enunciado e imagen de p3 de la tarea 3 de 2026.tex` (use its figures verbatim when available — don't redraw).

**Kirchhoff problem-solving method** (branch-current method — `Solucion_tarea3_P2/P3`, `Solucion_clase_12-06-2026`):
1. **Simplify first**: reduce series/parallel resistor groups to equivalents (e.g. `18∥9∥3 = 2Ω`) and draw the reduced schematic, before applying Kirchhoff.
2. **KCL** at the node: one current-balance equation (e.g. `I₁ + I₂ = I₃`), read from the assumed current-arrow directions.
3. **KVL** per independent mesh (M₁, M₂): ΣEMF = ΣIR with signs from source polarities + traversal direction. Keep the professor's explicit form first (e.g. `4I₁ − 12 + 2I₁ − 6 − 6I₂ = 0`) then simplify.
4. **Solve** by substitution; **verify** with the node equation and a power balance (Σε·I delivered = ΣI²R dissipated).
5. A negative current ⇒ real direction opposite the assumed one.

**Magnetic force/torque on a current loop** (`Solucion_tarea3_P4`, `Solucion_clase_12-06-2026` Prob 3):
- Force per straight side `F = I L × B` (`L` = side length in the current direction). Net force on a closed loop in a **uniform** field is **zero** (check: opposite sides cancel).
- Moment `μ = I A n̂` (`n̂` from right-hand rule on the circulation); torque `τ = μ × B` (only B⊥μ contributes).
- The current circulation read from the figure sets the sign of μ and τ — **state the assumed direction explicitly** (see figure workflow below).

**Correcting TikZ figures — mandatory workflow:**
1. Read the PDF enunciado figure first (`guia[N].pdf`, `guia_tarea[N]_*.pdf`, etc.).
2. Extract ALL charge/object positions from the figure and present them to the user in a table.
3. Wait for explicit confirmation before doing any recalculation.
4. Only then rewrite the TikZ and recompute all quantities that depend on the corrected positions.
> Reason: a single wrong position cascades into errors in every force/field calculation. Fixing only the reported position without verifying the others generates a second round of corrections.

**Long equations — formatting rule**: chains of 3+ chained equalities (fraction → coefficient × vector → component result) must use `align*` with `\\` line breaks between steps, never a single `equation*`. Single-line equation* causes overflow past the right margin in the compiled PDF.

**LaTeX build artifacts** (`.aux`, `.log`, `.bbl`, `.blg`) in `corpus/` are currently tracked in git (committed before gitignore rules were added). Do not delete them manually; leave them as-is unless doing an explicit cleanup with `git rm --cached`.

## Notes

- API key: `.env` file with `ANTHROPIC_API_KEY`
- Session logs: `.claude/logs/YYYY-MM-DD_session_log.md`
- Textbook PDFs (Sears, Serway) are gitignored due to copyright
- Planned features (MCP server, SymPy math tools, field visualization, tutor mode): see `ROADMAP.md`
- Git remote must include the username to avoid 403 auth errors:
  ```bash
  git remote set-url origin https://arturama-cmd@github.com/arturama-cmd/electro_agent.git
  ```
