# 🚀 Roadmap: Agente Avanzado de Electromagnetismo

> Plan de desarrollo para transformar el agente en un sistema robusto con capacidades matemáticas, visualización y MCP Server

---

## 🎯 Objetivos del Proyecto

1. **Razonamiento matemático riguroso** con SymPy para validación vectorial
2. **MCP Server** para gestión eficiente de libros y documentación
3. **Visualización de campos** usando teoremas de Gauss y Stokes
4. **Tool Use de Claude** para cálculos automáticos y validación física

---

## 🏗️ Arquitectura Propuesta

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit UI                          │
└───────────────────┬─────────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────────┐
│              Claude Agent (Orchestrator)                 │
│  - Tool Use enabled                                      │
│  - Agentic RAG                                          │
└─┬──────────┬──────────┬──────────┬──────────────────────┘
  │          │          │          │
  │          │          │          │
┌─▼──────┐ ┌▼────────┐ ┌▼───────┐ ┌▼─────────────────────┐
│ MCP    │ │ Vector  │ │SymPy   │ │ Visualization Tools  │
│ Server │ │Database │ │Tools   │ │ - matplotlib         │
│        │ │(Chroma) │ │        │ │ - plotly             │
│ - PDFs │ │         │ │-Vector │ │ - mayavi (3D)        │
│ - LaTeX│ │ - .tex  │ │ calc   │ │                      │
│ - Books│ │ - docs  │ │-Maxwell│ │ Gauss/Stokes        │
│        │ │         │ │ eqs    │ │ visualization        │
└────────┘ └─────────┘ └────────┘ └──────────────────────┘
```

---

## 📊 Fases de Implementación

### **FASE 1: Herramientas Matemáticas** 🧮
**Duración:** Semana 1-2
**Prioridad:** ALTA ⚡

#### 1.1 Sistema de Cálculo Vectorial con SymPy

**Archivo a crear:** `math_tools.py`

**Funciones a implementar:**

- [ ] `calculate_electric_field(charges, point)` - Campo eléctrico de múltiples cargas
  - Input: Lista de cargas [(q, x, y, z), ...], punto (x, y, z)
  - Output: Vector E = (Ex, Ey, Ez)

- [ ] `find_zero_field_points(charges)` - Encontrar puntos donde E=0
  - **CRÍTICO:** Incluir validación física de soluciones
  - Verificar direcciones de vectores
  - Eliminar soluciones no físicas

- [ ] `verify_solution_physically(charges, point)` - Validar solución
  - Verificar si los vectores se cancelan correctamente
  - Retornar `(is_valid: bool, reason: str)`

- [ ] `vector_operations`
  - `dot_product(v1, v2)` - Producto punto
  - `cross_product(v1, v2)` - Producto cruz
  - `magnitude(v)` - Magnitud
  - `normalize(v)` - Vector unitario

- [ ] `field_operations` (Teoremas fundamentales)
  - `divergence(field, point)` - ∇·E (Teorema de Gauss)
  - `curl(field, point)` - ∇×E (Teorema de Stokes)
  - `gradient(scalar_field, point)` - ∇φ

**Tecnologías:**
- SymPy 1.14+ para cálculo simbólico
- NumPy para cálculo numérico
- SciPy para integración numérica

**Tests a crear:**
```python
# tests/test_math_tools.py
def test_opposite_charges_zero_field():
    """Verifica que cargas opuestas tienen E=0 fuera del segmento"""
    charges = [(5e-6, -6.5, 0, 0), (-9e-6, -4.1, 0, 0)]
    points = find_zero_field_points(charges)
    assert all(p < -6.5 or p > -4.1 for p in points)  # Fuera del segmento

def test_same_sign_charges_zero_field():
    """Verifica que cargas del mismo signo tienen E=0 entre ellas"""
    charges = [(5e-6, -6.5, 0, 0), (9e-6, -4.1, 0, 0)]
    points = find_zero_field_points(charges)
    assert any(-6.5 < p < -4.1 for p in points)  # Entre las cargas
```

---

#### 1.2 Integración con Claude Tool Use

**Archivo a crear:** `claude_tools.py`

**Tools a definir:**

```python
MATH_TOOLS = [
    {
        "name": "calculate_electric_field",
        "description": "Calcula el campo eléctrico en un punto dado múltiples cargas puntuales. Retorna el vector campo eléctrico.",
        "input_schema": {
            "type": "object",
            "properties": {
                "charges": {
                    "type": "array",
                    "description": "Lista de cargas [(q1, x1, y1, z1), ...]",
                    "items": {
                        "type": "array",
                        "items": {"type": "number"}
                    }
                },
                "point": {
                    "type": "array",
                    "description": "Punto donde calcular el campo [x, y, z]",
                    "items": {"type": "number"}
                }
            },
            "required": ["charges", "point"]
        }
    },
    {
        "name": "find_field_zero_points",
        "description": "Encuentra todos los puntos donde el campo eléctrico se anula y valida físicamente cada solución. IMPORTANTE: Verifica las direcciones de los vectores de campo.",
        "input_schema": {
            "type": "object",
            "properties": {
                "charges": {
                    "type": "array",
                    "description": "Lista de cargas [(q1, x1, y1, z1), ...]"
                }
            },
            "required": ["charges"]
        }
    },
    {
        "name": "verify_vector_directions",
        "description": "Verifica las direcciones de los vectores de campo eléctrico en un punto para validar si pueden cancelarse.",
        "input_schema": {
            "type": "object",
            "properties": {
                "charges": {"type": "array"},
                "point": {"type": "array"}
            },
            "required": ["charges", "point"]
        }
    },
    {
        "name": "calculate_divergence",
        "description": "Calcula la divergencia de un campo vectorial (Ley de Gauss: ∇·E = ρ/ε₀)",
        "input_schema": {...}
    },
    {
        "name": "calculate_curl",
        "description": "Calcula el rotacional de un campo vectorial (Ley de Faraday: ∇×E = -∂B/∂t)",
        "input_schema": {...}
    }
]
```

**Modificar:** `rag_system.py`
```python
# Agregar tools al mensaje de Claude
response = self.anthropic_client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=4096,
    tools=MATH_TOOLS,  # ← NUEVO
    system=system_prompt,
    messages=messages
)

# Manejar tool calls
if response.stop_reason == "tool_use":
    # Ejecutar tool
    # Enviar resultado de vuelta a Claude
    # Obtener respuesta final
```

**Beneficio:** Claude podrá:
- Calcular campos automáticamente
- Validar soluciones físicamente
- Detectar errores en razonamiento vectorial
- Generar explicaciones paso a paso con cálculos verificados

---

### **FASE 2: MCP Server para Documentación** 📚
**Duración:** Semana 2-3
**Prioridad:** ALTA

#### 2.1 Implementar MCP Server

**Estructura de directorios:**
```
mcp_server/
├── __init__.py
├── server.py                 # MCP server principal
├── config.py                 # Configuración
├── processors/
│   ├── __init__.py
│   ├── pdf_processor.py      # Procesador de PDFs
│   ├── latex_processor.py    # Procesador de LaTeX (mejorado)
│   ├── epub_processor.py     # Procesador de ePub
│   └── equation_extractor.py # Extractor de ecuaciones
├── tools/
│   ├── __init__.py
│   ├── search.py             # Búsqueda semántica
│   ├── extract.py            # Extracción de secciones
│   └── index.py              # Indexación de documentos
└── storage/
    ├── __init__.py
    └── vector_store.py       # Interfaz con ChromaDB
```

**Archivo:** `mcp_server/server.py`

```python
from mcp.server import Server
from mcp.types import Tool, TextContent

app = Server("electromagnetism-docs")

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="search_textbook",
            description="Busca información en libros de electromagnetismo",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "book": {"type": "string", "enum": ["griffiths", "purcell", "jackson", "hayt", "all"]},
                    "chapter": {"type": "integer", "optional": True}
                }
            }
        ),
        Tool(
            name="get_equation",
            description="Obtiene una ecuación específica con su contexto",
            inputSchema={
                "type": "object",
                "properties": {
                    "equation_name": {"type": "string"},
                    "include_derivation": {"type": "boolean"}
                }
            }
        ),
        Tool(
            name="get_theorem",
            description="Obtiene un teorema completo (enunciado, demostración, aplicaciones)",
            inputSchema={...}
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "search_textbook":
        return await search_textbook(**arguments)
    elif name == "get_equation":
        return await get_equation(**arguments)
    # ...
```

**Procesadores:**

- [ ] `pdf_processor.py`
  - Usar PyMuPDF para extracción de texto
  - Detectar ecuaciones (regex + OCR si es necesario)
  - Extraer figuras y diagramas
  - Mantener estructura de capítulos/secciones

- [ ] `equation_extractor.py`
  - Detectar ecuaciones en LaTeX
  - Extraer ecuaciones de Maxwell
  - Indexar por nombre/tipo
  - Incluir contexto (definiciones de variables)

- [ ] `latex_processor.py` (mejorado)
  - Mantener notación matemática
  - Preservar estructura lógica
  - Mejorar limpieza de comandos

**Libros a indexar:**
1. ✅ Griffiths - "Introduction to Electrodynamics" (prioridad 1)
2. ✅ Purcell - "Electricity and Magnetism" (prioridad 2)
3. ⏳ Jackson - "Classical Electrodynamics" (prioridad 3)
4. ⏳ Hayt - "Engineering Electromagnetics" (prioridad 4)

---

#### 2.2 Integración con RAG existente

**Modificar:** `rag_system.py`

```python
class ElectromagnetismRAG:
    def __init__(self):
        # ... existing code ...

        # NUEVO: Cliente MCP
        self.mcp_client = MCPClient("http://localhost:8000")

    async def retrieve_from_mcp(self, query: str, source: str = "all"):
        """Recupera información desde MCP server"""
        result = await self.mcp_client.call_tool(
            "search_textbook",
            {"query": query, "book": source}
        )
        return result

    def generate_response(self, user_question: str):
        # Usar tanto ChromaDB como MCP
        local_problems = self.retrieve_relevant_problems(user_question)
        textbook_content = await self.retrieve_from_mcp(user_question)

        # Combinar contextos
        context = self._build_context(local_problems, textbook_content)
        # ...
```

**Metadatos enriquecidos:**
```python
{
    "source": "griffiths",
    "chapter": 2,
    "section": "2.3",
    "page": 65,
    "topic": "Gauss's Law",
    "equations": ["gauss_law_integral", "gauss_law_differential"],
    "difficulty": "intermediate",
    "related_theorems": ["divergence_theorem"]
}
```

---

### **FASE 3: Visualización de Campos** 📊
**Duración:** Semana 3-4
**Prioridad:** MEDIA

#### 3.1 Visualización 2D

**Archivo:** `visualization/fields_2d.py`

**Funciones a implementar:**

- [ ] `plot_electric_field_lines(charges, xlim, ylim)`
  - Líneas de campo eléctrico
  - Dirección indicada con flechas
  - Color según intensidad

- [ ] `plot_equipotential_surfaces(charges, xlim, ylim)`
  - Curvas equipotenciales
  - Niveles personalizables
  - Relación perpendicular con líneas de campo

- [ ] `plot_field_vectors(field_func, region)`
  - Campo vectorial con quiver plot
  - Normalización opcional
  - Grid personalizable

- [ ] `visualize_gauss_law_2d(surface, charges_inside)`
  - Superficie gaussiana (círculo, rectángulo)
  - Flujo calculado y visualizado
  - Comparación con Q_enc/ε₀

**Ejemplo de uso:**
```python
from visualization.fields_2d import plot_electric_field_lines

charges = [(5e-6, -2, 0), (-5e-6, 2, 0)]  # Dipolo
fig = plot_electric_field_lines(
    charges,
    xlim=(-5, 5),
    ylim=(-5, 5),
    num_lines=20,
    show_charges=True
)
fig.savefig("dipole_field.png")
```

---

#### 3.2 Visualización 3D

**Archivo:** `visualization/fields_3d.py`

**Funciones:**

- [ ] `plot_3d_field_vectors(field_func, volume)`
  - Campo vectorial 3D interactivo
  - Rotación y zoom
  - Plotly para interactividad

- [ ] `plot_flux_through_surface(field, surface)`
  - Superficie gaussiana 3D (esfera, cilindro, cubo)
  - Flujo a través de la superficie
  - Vectores normales a la superficie
  - Animación del flujo

- [ ] `plot_circulation(field, path)`
  - Camino cerrado en 3D
  - Circulación calculada
  - Visualización de ∮E·dl

- [ ] `animate_field_evolution(field_func_time, duration)`
  - Campos dependientes del tiempo
  - Útil para ondas electromagnéticas
  - Exportar a GIF/MP4

**Tecnologías:**
- Plotly para gráficos interactivos 3D
- Mayavi para campos vectoriales densos
- Matplotlib para exportación estática

---

#### 3.3 Integración con Claude Tool Use

**Agregar a:** `claude_tools.py`

```python
VISUALIZATION_TOOLS = [
    {
        "name": "visualize_electric_field",
        "description": "Genera visualización del campo eléctrico para un conjunto de cargas",
        "input_schema": {
            "type": "object",
            "properties": {
                "charges": {"type": "array"},
                "plot_type": {
                    "type": "string",
                    "enum": ["field_lines", "vectors", "equipotential", "3d_vectors"]
                },
                "xlim": {"type": "array"},
                "ylim": {"type": "array"}
            }
        }
    },
    {
        "name": "visualize_gauss_law",
        "description": "Visualiza la aplicación de la Ley de Gauss con superficie gaussiana",
        "input_schema": {
            "type": "object",
            "properties": {
                "surface_type": {"enum": ["sphere", "cylinder", "box"]},
                "charges": {"type": "array"},
                "surface_params": {"type": "object"}
            }
        }
    },
    {
        "name": "visualize_stokes_theorem",
        "description": "Visualiza la aplicación del Teorema de Stokes",
        "input_schema": {...}
    }
]
```

**Flujo de trabajo:**
1. Usuario pregunta: "Muéstrame el campo de un dipolo"
2. Claude llama `visualize_electric_field`
3. Sistema genera imagen
4. Imagen se guarda en `temp/`
5. Claude recibe ruta de imagen
6. Streamlit muestra imagen en chat

---

### **FASE 4: Interfaz Avanzada** 🖥️
**Duración:** Semana 4-5
**Prioridad:** MEDIA

#### 4.1 Streamlit Mejorado

**Archivo:** `app_advanced.py`

**Nuevas características:**

- [ ] **Panel de visualizaciones**
  - Mostrar imágenes generadas inline
  - Galería de visualizaciones anteriores
  - Descarga de imágenes en alta resolución

- [ ] **Panel de cálculos paso a paso**
  ```
  📊 Cálculos realizados:
  ├─ Campo de q₁ en P: E₁ = (1500, 0, 0) N/C
  ├─ Campo de q₂ en P: E₂ = (-1500, 0, 0) N/C
  └─ Campo total: E_total = (0, 0, 0) N/C ✓
  ```

- [ ] **Editor interactivo de problemas**
  - Formulario para definir cargas
  - Preview de configuración
  - Botón "Resolver" → Claude procesa

- [ ] **Exportación**
  - PDF con solución completa
  - LaTeX source code
  - Imágenes incluidas

**Sidebar mejorado:**
```python
with st.sidebar:
    st.header("⚙️ Configuración")

    # Seleccionar modo
    mode = st.selectbox("Modo", ["Chat", "Tutor", "Explorador"])

    # Fuentes de conocimiento
    st.subheader("📚 Fuentes")
    use_textbooks = st.checkbox("Libros de texto", value=True)
    use_local_problems = st.checkbox("Problemas locales", value=True)

    # Visualización
    st.subheader("📊 Visualización")
    auto_visualize = st.checkbox("Auto-generar gráficos", value=False)

    # Herramientas matemáticas
    st.subheader("🧮 Matemáticas")
    enable_symbolic = st.checkbox("Cálculo simbólico", value=True)
    validate_physics = st.checkbox("Validación física", value=True)
```

---

#### 4.2 Modo "Tutor"

**Características:**

- [ ] **Preguntas guiadas**
  - "¿Qué dirección tiene el campo de q₁ en este punto?"
  - "¿Pueden cancelarse estos vectores? ¿Por qué?"

- [ ] **Validación de respuestas**
  - Estudiante responde
  - Claude valida (usando tools de cálculo)
  - Feedback inmediato

- [ ] **Hints progresivos**
  - Nivel 1: Hint conceptual
  - Nivel 2: Hint con ecuación
  - Nivel 3: Primer paso de solución

- [ ] **Generación de problemas similares**
  - Basado en problema actual
  - Dificultad ajustable
  - Soluciones disponibles

**Interfaz:**
```python
if mode == "Tutor":
    st.info("🎓 Modo Tutor: Aprende paso a paso")

    # Problema actual
    st.markdown("### Problema")
    st.write(current_problem)

    # Respuesta del estudiante
    student_answer = st.text_area("Tu respuesta:")

    if st.button("Verificar"):
        # Claude valida usando tools
        validation = validate_student_answer(student_answer, correct_answer)

        if validation["correct"]:
            st.success("¡Correcto! " + validation["feedback"])
        else:
            st.error("No del todo. " + validation["hint"])
```

---

### **FASE 5: Testing y Optimización** ✅
**Duración:** Semana 5-6
**Prioridad:** ALTA

#### 5.1 Tests Unitarios

**Estructura:**
```
tests/
├── test_math_tools.py          # Tests de cálculos
├── test_visualization.py       # Tests de visualización
├── test_mcp_server.py         # Tests del MCP server
├── test_rag_system.py         # Tests del RAG
└── test_integration.py        # Tests end-to-end
```

**Cobertura mínima:** 80%

**Tests críticos:**
- ✅ Validación física de soluciones
- ✅ Cálculo de campos eléctricos
- ✅ Búsqueda en MCP server
- ✅ Generación de visualizaciones
- ✅ Integración Claude tools

---

#### 5.2 Documentación

**Archivos a crear/actualizar:**

- [ ] `API.md` - Documentación de la API del MCP server
- [ ] `TOOLS.md` - Documentación de todas las tools de Claude
- [ ] `EXAMPLES.md` - Ejemplos de uso del sistema
- [ ] `CONTRIBUTING.md` - Guía para contribuir
- [ ] Actualizar `README.md` con nuevas características

---

#### 5.3 Optimización

**Áreas a optimizar:**

- [ ] **Caché de cálculos**
  - Guardar resultados de cálculos frecuentes
  - Evitar recalcular campos idénticos

- [ ] **Lazy loading de libros**
  - Cargar libros solo cuando se necesiten
  - Reducir tiempo de inicio

- [ ] **Compresión de embeddings**
  - Reducir tamaño de ChromaDB
  - Mantener precisión

- [ ] **Batch processing**
  - Procesar múltiples consultas en paralelo
  - Usar asyncio para MCP calls

---

## 📈 Cronograma Detallado

| Semana | Fase | Tareas Principales | Entregables |
|--------|------|-------------------|-------------|
| **1** | Matemáticas | • Implementar `math_tools.py`<br>• Crear validación física<br>• Tests unitarios | ✅ Sistema de cálculo vectorial<br>✅ Validación automática |
| **2** | Tool Use + MCP inicio | • Integrar tools con Claude<br>• Crear estructura MCP<br>• Procesador PDF básico | ✅ Claude con tools matemáticas<br>✅ MCP server base |
| **3** | MCP completo | • Procesar 4 libros<br>• Búsqueda semántica<br>• Extracción de ecuaciones | ✅ Base de conocimiento completa<br>✅ MCP tools funcionales |
| **4** | Visualización 2D | • Líneas de campo<br>• Equipotenciales<br>• Ley de Gauss 2D | ✅ Visualizaciones 2D<br>✅ Integración con Claude |
| **5** | Visualización 3D + UI | • Campos 3D interactivos<br>• Interfaz mejorada<br>• Modo tutor | ✅ Sistema completo<br>✅ UI avanzada |
| **6** | Testing + Docs | • Tests unitarios (80%)<br>• Documentación completa<br>• Optimización | ✅ Sistema en producción<br>✅ Documentación |

---

## 🔧 Stack Tecnológico Completo

### Core
```
├── Python 3.11+
├── Claude 4.5 (con Tool Use + Programmatic Calling)
├── MCP SDK 1.0+
└── Anthropic SDK 0.40+
```

### Matemáticas
```
├── SymPy 1.14+ (cálculo simbólico)
├── NumPy 1.26+ (cálculo numérico)
└── SciPy 1.12+ (integración, optimización)
```

### Visualización
```
├── matplotlib 3.8+ (gráficos 2D)
├── plotly 5.18+ (gráficos 3D interactivos)
└── mayavi 4.8+ (campos vectoriales 3D avanzados)
```

### Procesamiento de Documentos
```
├── PyMuPDF (fitz) 1.23+ (PDFs)
├── pypdf2 3.0+ (extracción de texto)
├── ebooklib 0.18+ (ePub)
└── python-docx 1.1+ (Word)
```

### RAG & Vector DB
```
├── ChromaDB 0.4.22+
├── sentence-transformers 2.2+
└── LangChain 0.1+ (opcional, para orquestación)
```

### Web & UI
```
├── Streamlit 1.31+
├── FastAPI 0.109+ (para MCP server)
└── uvicorn 0.27+ (ASGI server)
```

---

## 🎯 Entregables Finales

Al completar todas las fases, el sistema tendrá:

### 1. Validación Matemática Automática ✅
- Cálculo de campos eléctricos y magnéticos
- Validación física de soluciones (direcciones de vectores)
- Eliminación automática de soluciones no físicas
- Explicaciones paso a paso con cálculos verificados

### 2. Base de Conocimiento Completa 📚
- 4 libros de texto completos indexados
- Búsqueda semántica avanzada
- Extracción de ecuaciones con contexto
- Teoremas con demostraciones

### 3. Visualizaciones On-Demand 📊
- Campos eléctricos 2D/3D
- Superficies equipotenciales
- Ley de Gauss con superficies gaussianas
- Teorema de Stokes con circulación
- Animaciones de campos dependientes del tiempo

### 4. MCP Server Reutilizable 🔌
- API REST completa
- Procesamiento multi-formato (PDF, LaTeX, ePub)
- Caché inteligente
- Escalable a otros dominios

### 5. Interfaz Pedagógica 🎓
- Modo tutor con validación de respuestas
- Generador de problemas similares
- Hints progresivos
- Exportación a PDF/LaTeX

### 6. Herramientas de Claude 🤖
- 15+ tools matemáticas
- 8+ tools de visualización
- 5+ tools de búsqueda (MCP)
- Orquestación automática

---

## 🚀 Quick Start - Fase 1

### Esta Semana: Herramientas Matemáticas

```bash
# 1. Crear estructura
mkdir -p math_tools visualization mcp_server/processors tests

# 2. Instalar dependencias
pip install sympy numpy scipy matplotlib pytest

# 3. Crear archivo base
touch math_tools.py
touch tests/test_math_tools.py
```

### Ejemplo de implementación inicial

**`math_tools.py`** (versión inicial):
```python
"""
Herramientas matemáticas para cálculos de electromagnetismo.
"""
import numpy as np
from sympy import symbols, solve, sqrt
from typing import List, Tuple, Dict

def calculate_electric_field(charges: List[Tuple], point: Tuple) -> np.ndarray:
    """
    Calcula el campo eléctrico en un punto dado múltiples cargas.

    Args:
        charges: Lista de tuplas (q, x, y, z) en Coulombs y metros
        point: Tupla (x, y, z) del punto de observación

    Returns:
        Vector E = (Ex, Ey, Ez) en N/C
    """
    k = 8.99e9  # Constante de Coulomb
    E_total = np.array([0.0, 0.0, 0.0])

    for charge in charges:
        q, qx, qy, qz = charge
        px, py, pz = point

        # Vector de la carga al punto
        r = np.array([px - qx, py - qy, pz - qz])
        r_mag = np.linalg.norm(r)

        if r_mag < 1e-10:
            continue  # Evitar división por cero

        # Campo de esta carga
        E = k * q * r / (r_mag ** 3)
        E_total += E

    return E_total

def find_zero_field_points(charges: List[Tuple]) -> Dict:
    """
    Encuentra puntos donde E = 0 y valida físicamente.

    Args:
        charges: Lista de cargas [(q1, x1, y1, z1), ...]

    Returns:
        Dict con soluciones válidas y razón física
    """
    # Implementar búsqueda simbólica + validación
    # TODO: Próxima implementación
    pass

# ... más funciones
```

---

## 📚 Referencias y Recursos

### MCP (Model Context Protocol)
- [Integrating Agentic RAG with MCP Servers](https://becomingahacker.org/integrating-agentic-rag-with-mcp-servers-technical-implementation-guide-1aba8fd4e442)
- [MCP Implementation using RAG Guide](https://www.projectpro.io/article/mcp-with-rag/1144)
- [Multi-Document RAG MCP Server](https://www.pulsemcp.com/servers/anuragb7-multi-document-rag)
- [Mastering MCP Servers in 2025](https://superagi.com/mastering-mcp-servers-in-2025-a-beginners-guide-to-model-context-protocol-implementation/)

### Matemáticas Simbólicas
- [SymPy Vector Calculus Documentation](https://docs.sympy.org/latest/modules/vector/index.html)
- [SymPy Scalar and Vector Fields](https://docs.sympy.org/latest/modules/vector/fields.html)
- [GitHub - Vector Analysis with Python/SymPy](https://github.com/Hese49/Vector-Analysis)

### Claude AI
- [Claude Tool Use Documentation](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
- [Advanced Tool Use with Claude](https://www.anthropic.com/engineering/advanced-tool-use)
- [Claude 4.5 Function Calling](https://composio.dev/blog/claude-function-calling-tools)

### Visualización Científica
- [Matplotlib Documentation](https://matplotlib.org/stable/index.html)
- [Plotly Python](https://plotly.com/python/)
- [Mayavi Documentation](https://docs.enthought.com/mayavi/mayavi/)

---

## 📝 Notas de Implementación

### Prioridades
1. **CRÍTICO:** Validación física de soluciones (Fase 1)
2. **ALTA:** MCP server básico (Fase 2)
3. **MEDIA:** Visualizaciones 2D (Fase 3)
4. **BAJA:** Optimizaciones avanzadas (Fase 5)

### Decisiones de Arquitectura
- **¿Por qué MCP en lugar de RAG directo?**
  - Separación de responsabilidades
  - Reutilizable en otros proyectos
  - Escalable a múltiples fuentes de datos
  - Estándar de la industria en 2025

- **¿Por qué SymPy en lugar de cálculo numérico puro?**
  - Permite validación simbólica
  - Genera expresiones algebraicas
  - Útil para explicaciones pedagógicas
  - Detección de casos especiales

### Riesgos y Mitigaciones
- **Riesgo:** Procesamiento de PDFs puede fallar
  - **Mitigación:** Múltiples backends (PyMuPDF, pdfplumber)

- **Riesgo:** Visualizaciones 3D pueden ser lentas
  - **Mitigación:** Caché de renders, resolución ajustable

- **Riesgo:** MCP server puede sobrecargar memoria
  - **Mitigación:** Lazy loading, límites de memoria

---

## 🎓 Próximos Pasos Inmediatos

### Acción 1: Configurar entorno (Hoy)
```bash
cd /home/dell/Escritorio/electro_agent
source venv/bin/activate
pip install sympy numpy scipy matplotlib plotly pytest
mkdir -p math_tools visualization mcp_server tests
```

### Acción 2: Implementar validación física (Mañana)
- Crear `math_tools.py`
- Implementar `verify_solution_physically()`
- Agregar tests para casos conocidos

### Acción 3: Integrar con Claude (Esta semana)
- Modificar `rag_system.py`
- Agregar `claude_tools.py`
- Probar con el problema de las dos cargas

---

**Última actualización:** 2025-12-30
**Versión:** 1.0
**Estado:** En planificación
