# 🚀 Guía de Inicio Rápido

## Opción 1: Usando el script de inicio (Recomendado)

```bash
./run.sh
```

## Opción 2: Manual

```bash
# Activar entorno virtual
source venv/bin/activate

# Ejecutar aplicación
streamlit run app.py
```

## Primera Ejecución

La primera vez que ejecutes la aplicación:

1. ChromaDB descargará un modelo de embeddings (~79 MB) - esto es normal
2. El sistema indexará automáticamente los archivos .tex (tomará unos segundos)
3. La aplicación se abrirá en tu navegador en `http://localhost:8501`

## Probando el Sistema

Una vez que la aplicación esté corriendo, prueba con estas preguntas:

- "¿Cómo se calculan capacitores en serie y paralelo?"
- "Explícame las leyes de Kirchhoff"
- "¿Cómo se calcula el campo eléctrico de una carga puntual?"
- "Dame un ejemplo de análisis de circuitos"

## Estructura de Archivos

```
electro_agent/
├── app.py              # Interfaz Streamlit (INICIO AQUÍ)
├── rag_system.py       # Sistema RAG con ChromaDB
├── tex_processor.py    # Procesador de archivos LaTeX
├── run.sh             # Script de inicio
├── .env               # Tu API key (ya configurado)
├── requirements.txt   # Dependencias
└── chroma_db/        # Base de datos (generada automáticamente)
```

## Agregar Más Problemas

Para agregar nuevos problemas al sistema:

1. Coloca tus archivos `.tex` en este directorio
2. Elimina la carpeta `chroma_db`
3. Reinicia la aplicación (se reindexará automáticamente)

## Troubleshooting

**Error: ANTHROPIC_API_KEY no encontrada**
→ Verifica que el archivo `.env` existe y contiene tu API key

**La aplicación no inicia**
→ Asegúrate de activar el entorno virtual: `source venv/bin/activate`

**ChromaDB da error**
→ Elimina la carpeta `chroma_db` y reinicia

## Detener la Aplicación

Presiona `Ctrl + C` en la terminal donde está corriendo Streamlit
