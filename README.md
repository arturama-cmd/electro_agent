# ⚡ Asistente de Electromagnetismo con IA

Agente conversacional inteligente para ayudar a estudiantes de ingeniería con electromagnetismo. Utiliza Claude 4.5 de Anthropic y un sistema RAG (Retrieval-Augmented Generation) para proporcionar respuestas científicamente rigurosas basadas en problemas resueltos.

## 🚀 Características

- **Respuestas rigurosas**: Basadas en las ecuaciones de Maxwell y leyes fundamentales del electromagnetismo
- **Sistema RAG**: Recupera problemas resueltos relevantes de archivos LaTeX
- **Interfaz conversacional**: Chat interactivo con Streamlit
- **Explicaciones paso a paso**: Muestra el desarrollo completo de soluciones
- **Base de conocimiento personalizada**: Indexa automáticamente tus archivos .tex

## 📋 Requisitos previos

- Python 3.8+
- Una API key de Anthropic (Claude)

## 🛠️ Instalación

1. **Clonar o navegar al directorio del proyecto**

```bash
cd /home/dell/Escritorio/electro_agent
```

2. **Crear y activar entorno virtual**

```bash
python -m venv venv
source venv/bin/activate  # En Linux/Mac
# o
venv\Scripts\activate  # En Windows
```

3. **Instalar dependencias**

```bash
pip install -r requirements.txt
```

4. **Configurar API key**

El archivo `.env` ya está configurado con tu API key de Anthropic. Si necesitas cambiarla:

```bash
# .env
ANTHROPIC_API_KEY=tu-api-key-aquí
```

## 🎯 Uso

### Ejecutar la aplicación

```bash
streamlit run app.py
```

La aplicación se abrirá en tu navegador en `http://localhost:8501`

### Indexar nuevos problemas

El sistema indexa automáticamente todos los archivos `.tex` en el directorio al iniciar por primera vez. Para agregar nuevos problemas:

1. Agrega tus archivos `.tex` al directorio
2. Elimina la carpeta `chroma_db` para reiniciar la indexación
3. Reinicia la aplicación

## 📚 Estructura del proyecto

```
electro_agent/
├── app.py                  # Interfaz Streamlit
├── rag_system.py           # Sistema RAG con ChromaDB
├── tex_processor.py        # Procesador de archivos LaTeX
├── requirements.txt        # Dependencias
├── .env                    # Variables de entorno
├── PROBLEMA 1.tex         # Problemas de capacitores
├── Problema_2.tex         # Problemas de circuitos y Kirchhoff
├── main.tex               # Problemas de campos eléctricos
└── chroma_db/             # Base de datos vectorial (generada automáticamente)
```

## 🎓 Tipos de problemas indexados

Actualmente el sistema tiene problemas sobre:

1. **Capacitores en circuitos**
   - Capacitores en serie y paralelo
   - Cálculo de capacitancia equivalente
   - Carga y voltaje en capacitores

2. **Circuitos y Leyes de Kirchhoff**
   - Reducción de circuitos
   - Leyes de Kirchhoff (corriente y voltaje)
   - Análisis de mallas y nodos
   - Potencia disipada en resistencias

3. **Cargas y Campos Eléctricos**
   - Campo eléctrico de cargas puntuales
   - Fuerzas eléctricas
   - Superposición de campos
   - Simetría y anulación de campos

## 💡 Ejemplos de uso

Puedes hacer preguntas como:

- "¿Cómo se calculan capacitores en serie y paralelo?"
- "Explícame las leyes de Kirchhoff"
- "¿Qué es el campo eléctrico de una carga puntual?"
- "¿Cómo se calcula la fuerza sobre una carga de prueba?"
- "Ayúdame a resolver un problema de circuitos con resistencias"

## 🔧 Personalización

### Agregar más conocimiento

Simplemente agrega archivos `.tex` con problemas resueltos al directorio. El sistema los procesará automáticamente.

### Modificar el comportamiento del asistente

Edita el `system_prompt` en `rag_system.py` (línea ~113) para cambiar el comportamiento del asistente.

### Ajustar el número de problemas recuperados

En `rag_system.py`, modifica el parámetro `n_results` en el método `generate_response()` (línea ~106).

## 🐛 Troubleshooting

**Error: "ANTHROPIC_API_KEY no encontrada"**
- Verifica que el archivo `.env` existe y contiene tu API key
- Asegúrate de que python-dotenv está instalado

**La aplicación no encuentra los archivos .tex**
- Verifica que los archivos `.tex` estén en el mismo directorio que `app.py`
- Revisa los permisos de lectura de los archivos

**ChromaDB da error**
- Elimina la carpeta `chroma_db` y reinicia la aplicación
- Verifica que tienes permisos de escritura en el directorio

## 📝 Roadmap futuro

- [ ] Visualización de campos electromagnéticos con matplotlib
- [ ] Soporte para ecuaciones de Maxwell con simbología LaTeX
- [ ] Exportar conversaciones a PDF
- [ ] Generar problemas personalizados
- [ ] Integración con herramientas de simulación (PyCharge, fdtd)

## 📄 Licencia

Este proyecto es de código abierto para fines educativos.

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Siéntete libre de:
- Agregar más problemas resueltos
- Mejorar el procesamiento de LaTeX
- Añadir visualizaciones
- Optimizar el sistema RAG

---

Desarrollado con ❤️ usando Claude 4.5, Streamlit y ChromaDB
