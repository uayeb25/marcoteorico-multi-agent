#!/bin/bash

# =====================================================
# Script de Instalación Automática
# Sistema Multiagente para Marco Teórico Académico
# =====================================================

set -e  # Salir si hay algún error

echo "🤖 Instalando Sistema Multiagente para Marco Teórico"
echo "=================================================="

# Función para verificar si un comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Verificar Python
echo "🐍 Verificando Python..."
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    echo "✅ Python encontrado: $PYTHON_VERSION"
    PYTHON_CMD="python3"
elif command_exists python; then
    PYTHON_VERSION=$(python --version 2>&1 | cut -d' ' -f2)
    echo "✅ Python encontrado: $PYTHON_VERSION"
    PYTHON_CMD="python"
else
    echo "❌ Error: Python no encontrado. Por favor instala Python 3.8+"
    exit 1
fi

# Verificar pip
echo "📦 Verificando pip..."
if command_exists pip3; then
    PIP_CMD="pip3"
elif command_exists pip; then
    PIP_CMD="pip"
else
    echo "❌ Error: pip no encontrado. Por favor instala pip"
    exit 1
fi

echo "✅ pip encontrado"

# Crear entorno virtual si no existe
echo "🏗️  Configurando entorno virtual..."
if [ ! -d "venv" ]; then
    echo "📁 Creando entorno virtual..."
    $PYTHON_CMD -m venv venv
    echo "✅ Entorno virtual creado"
else
    echo "✅ Entorno virtual ya existe"
fi

# Activar entorno virtual
echo "🔌 Activando entorno virtual..."
source venv/bin/activate
echo "✅ Entorno virtual activado"

# Actualizar pip
echo "⬆️  Actualizando pip..."
pip install --upgrade pip
echo "✅ pip actualizado"

# Instalar dependencias básicas
echo "📚 Instalando dependencias básicas..."
pip install -r requirements-minimal.txt
echo "✅ Dependencias básicas instaladas"

# Preguntar por instalación completa
read -p "¿Instalar dependencias completas? (incluye testing, linting, etc.) [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📚 Instalando dependencias completas..."
    pip install -r requirements.txt
    echo "✅ Dependencias completas instaladas"
fi

# Verificar Ollama
echo "🦙 Verificando Ollama..."
if command_exists ollama; then
    echo "✅ Ollama encontrado"
    
    # Verificar si el servidor está ejecutándose
    if ollama list >/dev/null 2>&1; then
        echo "✅ Servidor Ollama funcionando"
        
        # Verificar modelo llama3.2
        if ollama list | grep -q "llama3.2"; then
            echo "✅ Modelo llama3.2 disponible"
        else
            echo "🔽 Descargando modelo llama3.2..."
            ollama pull llama3.2:latest
            echo "✅ Modelo llama3.2 descargado"
        fi
    else
        echo "⚠️  Servidor Ollama no está ejecutándose"
        echo "   Ejecuta: ollama serve"
    fi
else
    echo "⚠️  Ollama no encontrado"
    echo "   Instala desde: https://ollama.ai/"
fi

# Crear carpetas necesarias
echo "📁 Creando estructura de carpetas..."
mkdir -p bibliografia
mkdir -p outputs
mkdir -p data/processed
mkdir -p config
echo "✅ Carpetas creadas"

# Verificar archivos de configuración
echo "⚙️  Verificando configuración..."
if [ ! -f "config/indice.txt" ]; then
    echo "📝 Creando archivo de índice por defecto..."
    cat > config/indice.txt << 'EOF'
2.1 Fundamentos Teóricos
2.1.1 Definiciones Conceptuales
2.1.2 Marco Conceptual
2.2 Variables de Estudio
2.2.1 Variable Dependiente
2.2.2 Variables Independientes
2.3 Antecedentes Empíricos
2.3.1 Estudios Nacionales
2.3.2 Estudios Internacionales
EOF
    echo "✅ Archivo índice creado"
fi

if [ ! -f "config/reglas_citas_apa.txt" ]; then
    echo "📖 Creando reglas APA por defecto..."
    cat > config/reglas_citas_apa.txt << 'EOF'
REGLAS DE CITACIÓN APA 7ma EDICIÓN

1. Citas en el texto:
   - (Autor, año)
   - Autor (año)

2. Referencias:
   - Libro: Autor, A. A. (año). Título del libro. Editorial.
   - Artículo: Autor, A. A. (año). Título del artículo. Revista, vol(num), páginas.

3. Formato:
   - Sangría francesa en referencias
   - Orden alfabético por apellido
   - Itálicas en títulos de libros y revistas
EOF
    echo "✅ Reglas APA creadas"
fi

# Prueba básica del sistema
echo "🧪 Realizando prueba básica..."
if $PYTHON_CMD -c "import langchain, chromadb, ollama; print('✅ Importaciones exitosas')"; then
    echo "✅ Sistema listo para usar"
else
    echo "⚠️  Algunas dependencias podrían tener problemas"
fi

echo ""
echo "🎉 ¡Instalación completada!"
echo ""
echo "📋 Próximos pasos:"
echo "1. Activar entorno virtual: source venv/bin/activate"
echo "2. Verificar sistema: python main.py"
echo "3. Colocar PDFs en bibliografia/"
echo "4. Procesar bibliografía: python main.py --process-docs"
echo "5. Generar contenido: python generar.py section 2.1"
echo ""
echo "📚 Para más información, consulta el README.md"
