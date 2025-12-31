#!/bin/bash

# Script para ejecutar la aplicación Streamlit del asistente de electromagnetismo

echo "⚡ Iniciando Asistente de Electromagnetismo ⚡"
echo ""

# Activar entorno virtual
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✓ Entorno virtual activado"
else
    echo "❌ No se encontró el entorno virtual. Por favor ejecuta:"
    echo "   python -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Verificar que las dependencias estén instaladas
if ! python -c "import streamlit" 2>/dev/null; then
    echo "❌ Dependencias no encontradas. Instalando..."
    pip install -r requirements.txt
fi

# Verificar archivo .env
if [ ! -f ".env" ]; then
    echo "❌ Archivo .env no encontrado"
    echo "   Por favor crea un archivo .env con tu ANTHROPIC_API_KEY"
    exit 1
fi

echo ""
echo "🚀 Iniciando aplicación Streamlit..."
echo "   La aplicación se abrirá en tu navegador"
echo "   Presiona Ctrl+C para detener"
echo ""

# Ejecutar Streamlit
streamlit run app.py
