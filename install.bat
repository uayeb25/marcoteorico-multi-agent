@echo off
REM =====================================================
REM Script de Instalación Automática para Windows
REM Sistema Multiagente para Marco Teórico Académico
REM =====================================================

echo 🤖 Instalando Sistema Multiagente para Marco Teórico
echo ==================================================

REM Verificar Python
echo 🐍 Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error: Python no encontrado. Por favor instala Python 3.8+
    pause
    exit /b 1
)
echo ✅ Python encontrado

REM Verificar pip
echo 📦 Verificando pip...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error: pip no encontrado. Por favor instala pip
    pause
    exit /b 1
)
echo ✅ pip encontrado

REM Crear entorno virtual si no existe
echo 🏗️  Configurando entorno virtual...
if not exist "venv" (
    echo 📁 Creando entorno virtual...
    python -m venv venv
    echo ✅ Entorno virtual creado
) else (
    echo ✅ Entorno virtual ya existe
)

REM Activar entorno virtual
echo 🔌 Activando entorno virtual...
call venv\Scripts\activate.bat
echo ✅ Entorno virtual activado

REM Actualizar pip
echo ⬆️  Actualizando pip...
python -m pip install --upgrade pip
echo ✅ pip actualizado

REM Instalar dependencias básicas
echo 📚 Instalando dependencias básicas...
pip install -r requirements-minimal.txt
if %errorlevel% neq 0 (
    echo ❌ Error instalando dependencias básicas
    pause
    exit /b 1
)
echo ✅ Dependencias básicas instaladas

REM Preguntar por instalación completa
set /p FULL_INSTALL="¿Instalar dependencias completas? (incluye testing, linting, etc.) [y/N]: "
if /i "%FULL_INSTALL%"=="y" (
    echo 📚 Instalando dependencias completas...
    pip install -r requirements.txt
    echo ✅ Dependencias completas instaladas
)

REM Verificar Ollama
echo 🦙 Verificando Ollama...
ollama list >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Ollama no encontrado o no está ejecutándose
    echo    Instala desde: https://ollama.ai/
    echo    Después ejecuta: ollama serve
) else (
    echo ✅ Ollama encontrado y funcionando
    
    REM Verificar modelo llama3.2
    ollama list | findstr "llama3.2" >nul 2>&1
    if %errorlevel% neq 0 (
        echo 🔽 Descargando modelo llama3.2...
        ollama pull llama3.2:latest
        echo ✅ Modelo llama3.2 descargado
    ) else (
        echo ✅ Modelo llama3.2 disponible
    )
)

REM Crear carpetas necesarias
echo 📁 Creando estructura de carpetas...
if not exist "bibliografia" mkdir bibliografia
if not exist "outputs" mkdir outputs
if not exist "data\processed" mkdir data\processed
if not exist "config" mkdir config
echo ✅ Carpetas creadas

REM Verificar archivos de configuración
echo ⚙️  Verificando configuración...
if not exist "config\indice.txt" (
    echo 📝 Creando archivo de índice por defecto...
    (
        echo 2.1 Fundamentos Teóricos
        echo 2.1.1 Definiciones Conceptuales
        echo 2.1.2 Marco Conceptual
        echo 2.2 Variables de Estudio
        echo 2.2.1 Variable Dependiente
        echo 2.2.2 Variables Independientes
        echo 2.3 Antecedentes Empíricos
        echo 2.3.1 Estudios Nacionales
        echo 2.3.2 Estudios Internacionales
    ) > config\indice.txt
    echo ✅ Archivo índice creado
)

if not exist "config\reglas_citas_apa.txt" (
    echo 📖 Creando reglas APA por defecto...
    (
        echo REGLAS DE CITACIÓN APA 7ma EDICIÓN
        echo.
        echo 1. Citas en el texto:
        echo    - ^(Autor, año^)
        echo    - Autor ^(año^)
        echo.
        echo 2. Referencias:
        echo    - Libro: Autor, A. A. ^(año^). Título del libro. Editorial.
        echo    - Artículo: Autor, A. A. ^(año^). Título del artículo. Revista, vol^(num^), páginas.
        echo.
        echo 3. Formato:
        echo    - Sangría francesa en referencias
        echo    - Orden alfabético por apellido
        echo    - Itálicas en títulos de libros y revistas
    ) > config\reglas_citas_apa.txt
    echo ✅ Reglas APA creadas
)

REM Prueba básica del sistema
echo 🧪 Realizando prueba básica...
python -c "import langchain, chromadb, ollama; print('✅ Importaciones exitosas')" 2>nul
if %errorlevel% neq 0 (
    echo ⚠️  Algunas dependencias podrían tener problemas
) else (
    echo ✅ Sistema listo para usar
)

echo.
echo 🎉 ¡Instalación completada!
echo.
echo 📋 Próximos pasos:
echo 1. Activar entorno virtual: venv\Scripts\activate.bat
echo 2. Verificar sistema: python main.py
echo 3. Colocar PDFs en bibliografia\
echo 4. Procesar bibliografía: python main.py --process-docs
echo 5. Generar contenido: python generar.py section 2.1
echo.
echo 📚 Para más información, consulta el README.md

pause
