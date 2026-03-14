# Asistente de Electromagnetismo con IA

Agente conversacional inteligente para ayudar a estudiantes de ingenieria con electromagnetismo. Utiliza Claude Sonnet 4 de Anthropic y un sistema RAG (Retrieval-Augmented Generation) para proporcionar respuestas cientificamente rigurosas basadas en problemas resueltos.

## Caracteristicas

- **Respuestas rigurosas**: Basadas en las ecuaciones de Maxwell y leyes fundamentales del electromagnetismo
- **Sistema RAG**: Recupera problemas resueltos relevantes de archivos LaTeX y PDF
- **Generacion de soluciones**: Soluciones paso a paso con diagramas TikZ, analisis cualitativo y desarrollo matematico completo
- **Interfaz conversacional**: Chat interactivo con Streamlit
- **Filtrado por temas**: Busqueda contextualizada por categoria (Campo Electrico, Campo Magnetico, etc.)
- **Base de conocimiento personalizada**: Indexa automaticamente archivos .tex y .pdf del corpus

## Requisitos previos

- Python 3.8+
- Una API key de Anthropic (Claude)
- Tesseract OCR (para PDFs escaneados)
- Poppler (incluido en el repositorio para Windows)

## Instalacion

1. **Clonar el repositorio**

```bash
git clone <url-del-repositorio>
cd electro_agent
```

2. **Crear y activar entorno virtual**

```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

3. **Instalar dependencias**

```bash
pip install -r requirements.txt
```

4. **Configurar API key**

Crear archivo `.env` en la raiz del proyecto:

```bash
ANTHROPIC_API_KEY=tu-api-key-aqui
```

## Uso

### Ejecutar la aplicacion

```bash
streamlit run app.py
```

La aplicacion se abrira en tu navegador en `http://localhost:8501`

### Agregar nuevos documentos al corpus

**Opcion 1**: Agregar archivos a la carpeta correspondiente en `corpus/` y usar el boton "Reindexar Corpus" en la barra lateral.

**Opcion 2**: Para agregar un PDF individual sin reindexar todo:
```bash
# Editar add_single_pdf.py lineas 74-75 con la ruta y categoria
python add_single_pdf.py
```

## Contenido del Corpus

### Campo Electrico (`corpus/campo_electrico/`)

#### Examenes y Problemas
| Archivo | Descripcion |
|---------|-------------|
| `certamen1 - 2021_1_forma A.tex/pdf` | Certamen 1, Semestre 2021-1, Forma A |
| `certamen1 - 2022_1_rec.tex/pdf` | Certamen 1 Recuperativo, Semestre 2022-1 |
| `certamen1.tex/pdf` | Certamen 1, Semestre 2024 |
| `P1-C1-S1-2025.tex` | Problema 1, Certamen 1, Semestre 2025-1 |
| `P1-REC-C1-S1-2025.tex` | Problema 1 Recuperativo, Certamen 1, Semestre 2025-1 |

#### Soluciones Desarrolladas
| Archivo | Contenido |
|---------|-----------|
| `Solucion_Tema_I.tex/pdf` | Fuerza electrica entre cargas puntuales en configuracion circular. Incluye: diagrama TikZ, analisis cualitativo de interacciones, vectores de posicion, superposicion de fuerzas |
| `Solucion_Certamen1_2021_FormaA.tex/pdf` | Solucion completa del Certamen 1 (2021) |
| `Solucion_Certamen1_2022_Rec.tex/pdf` | Solucion completa del Certamen Recuperativo (2022) |
| `Solucion_Certamen1_2024.tex/pdf` | Solucion completa del Certamen 1 (2024) |

#### Material de Referencia (Libros de Texto)
| Archivo | Descripcion |
|---------|-------------|
| `campo electrico sears.pdf` | Capitulo de Campo Electrico - Fisica Universitaria (Sears & Zemansky) |
| `campo electrico serway.pdf` | Capitulo de Campo Electrico - Fisica para Ciencias e Ingenieria (Serway) |

### Campo Magnetico (`corpus/campo_magnetico/`)

#### Guias y Tareas
| Archivo | Descripcion |
|---------|-------------|
| `guia_tarea4.tex/pdf` | Guia de ejercicios Tarea 4: Campo Magnetico |
| `pauta tarea 4.pdf` | Pauta de correccion Tarea 4 |

#### Soluciones Desarrolladas
| Archivo | Contenido |
|---------|-----------|
| `Solucion_Tarea4_CampoMagnetico.tex/pdf` | Problemas de campo magnetico e induccion: conductores rectos, Ley de Biot-Savart, fuerza sobre cargas en movimiento, fuerza entre conductores |

### Categorias Planificadas (En desarrollo)

| Categoria | Carpeta | Estado |
|-----------|---------|--------|
| Circuitos en Corriente Directa | `corpus/corriente_directa/` | Pendiente |
| Circuitos en Corriente Alterna | `corpus/corriente_alterna/` | Pendiente |
| Maquinas Electricas | `corpus/maquinas_electricas/` | Pendiente |

## Estructura de las Soluciones

Las soluciones generadas en LaTeX siguen una estructura pedagogica:

1. **Enunciado del Problema**: Planteamiento con diagrama TikZ (2D o 3D)
2. **Datos Numericos**: Valores dados con unidades SI
3. **Analisis Cualitativo**: Direccion de fuerzas/campos, tipo de interaccion (atractiva/repulsiva)
4. **Desarrollo Matematico**:
   - Vectores de posicion
   - Aplicacion de leyes (Coulomb, Biot-Savart, Gauss, etc.)
   - Calculo paso a paso con unidades
5. **Resultado Final**: Respuesta encuadrada con `\boxed{}`
6. **Interpretacion Fisica**: Significado del resultado

## Ejemplos de Preguntas

- "Calcula la fuerza electrica entre tres cargas dispuestas en un triangulo"
- "Explica la ley de Gauss y como aplicarla a una esfera conductora"
- "Como determino el campo magnetico de un conductor recto infinito?"
- "Cual es la fuerza sobre una carga en movimiento dentro de un campo magnetico?"
- "Resuelve un problema de capacitores en serie y paralelo"

## Estructura del Proyecto

```
electro_agent/
├── app.py                  # Interfaz Streamlit
├── rag_system.py           # Sistema RAG con ChromaDB
├── tex_processor.py        # Procesador de archivos LaTeX
├── pdf_processor.py        # Procesador de PDFs (con OCR)
├── add_single_pdf.py       # Agregar PDFs individuales
├── requirements.txt        # Dependencias Python
├── .env                    # Variables de entorno (API key)
├── corpus/                 # Base de conocimiento
│   ├── campo_electrico/    # Problemas de campo electrico
│   ├── campo_magnetico/    # Problemas de campo magnetico
│   ├── corriente_directa/  # (planificado)
│   ├── corriente_alterna/  # (planificado)
│   └── maquinas_electricas/# (planificado)
├── chroma_db/              # Base de datos vectorial (auto-generada)
├── tessdata/               # Modelos OCR para espanol
└── poppler-24.08.0/        # Dependencia para PDF (Windows)
```

## Troubleshooting

**Error: "ANTHROPIC_API_KEY no encontrada"**
- Verifica que el archivo `.env` existe y contiene tu API key
- Asegurate de que python-dotenv esta instalado

**ChromaDB da error**
- Elimina la carpeta `chroma_db` y reinicia la aplicacion
- Verifica que tienes permisos de escritura en el directorio

**PDF escaneado no se procesa**
- Instala Tesseract OCR: `pip install pytesseract pdf2image`
- Windows: Descarga Tesseract desde https://github.com/UB-Mannheim/tesseract/wiki
- Verifica que la ruta en `pdf_processor.py` linea 25 es correcta

**Primera ejecucion muy lenta**
- Es normal: ChromaDB descarga el modelo de embeddings (~79 MB)
- Las siguientes ejecuciones seran mas rapidas

## Licencia

Este proyecto es de codigo abierto para fines educativos.

---

Desarrollado con Claude Sonnet 4, Streamlit y ChromaDB | Universidad del Bio-Bio
