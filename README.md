# 🤖 Sistema Multiagente para Marco Teórico Académico

Sistema inteligente de generación automática de marcos teóricos académicos utilizando múltiples agentes especializados y tecnología RAG (Retrieval-Augmented Generation).

## 📋 Descripción

Este proyecto implementa un sistema multiagente que automatiza la creación de marcos teóricos académicos de alta calidad, integrando análisis bibliográfico, generación de contenido sustantivo y formato APA profesional.

### 🎯 Características Principales

- **Sistema RAG Avanzado**: Procesamiento inteligente de bibliografía PDF con ChromaDB
- **Arquitectura Multiagente**: 4 agentes especializados trabajando en colaboración
- **Generación por Secciones**: Control granular sobre la generación de contenido
- **Formato APA Automático**: Cumplimiento de normas académicas internacionales
- **Variables Independientes**: Integración automática de variables de investigación
- **Control de Calidad**: Supervisión automática y mejora iterativa
- **Modelo Gemma2 27B**: Generación de contenido académico de alta calidad (1,500+ palabras por sección)
- **Contenido Limpio**: Sin artefactos técnicos ni comentarios de agente visibles

## 🏗️ Arquitectura del Sistema

### 🤖 Agentes Especializados

1. **Investigador** (`InvestigadorAgent`)
   - Análisis profundo de bibliografía
   - Identificación de variables independientes
   - Extracción de contenido relevante

2. **Editor de Fondo** (`EditorFondoAgent`)
   - Generación de contenido académico sustantivo
   - Conexión con variables independientes
   - Desarrollo teórico extenso (800-1200 palabras)

3. **Redactor de Forma** (`RedactorFormaAgent`)
   - Aplicación de formato APA
   - Estructura académica profesional
   - Revisión de estilo y coherencia

4. **Supervisor** (`SupervisorAgent`)
   - Control de calidad académica
   - Coherencia narrativa
   - Validación final de contenido

### 🗂️ Estructura del Proyecto

```
AgenteMarcoTeorico/
├── src/
│   ├── agents/                 # Agentes especializados
│   ├── models/                 # Esquemas y modelos de datos
│   ├── utils/                  # Utilidades (RAG, procesamiento)
│   └── workflow/               # Flujo de trabajo multiagente
├── bibliografia/               # PDFs fuente
├── config/                     # Archivos de configuración
├── outputs/                    # Contenido generado
├── data/                       # Base de datos vectorial
├── main.py                     # Sistema principal
├── generar.py                  # Generador por secciones
└── config.py                   # Configuración global
```

## 🚀 Instalación

### Prerequisitos

- **Python 3.8+**
- **Ollama** instalado y ejecutándose
- **Modelo Gemma2 27B** descargado
- **Hardware recomendado**: 16GB+ RAM (óptimo: 32GB+ para Gemma2 27B)
- **Espacio en disco**: ~15GB para el modelo Gemma2 27B

### 1. Clonar e Instalar

```bash
git clone <repository-url>
cd AgenteMarcoTeorico
pip install -r requirements.txt
```

### 2. Configurar Ollama

```bash
# Instalar Ollama (si no está instalado)
curl -fsSL https://ollama.ai/install.sh | sh

# Descargar modelo Gemma2 27B (recomendado para mejor calidad)
ollama pull gemma2:27b

# Ejecutar servidor Ollama
ollama serve
```

### 3. Preparar Bibliografía

```bash
# Colocar archivos PDF en la carpeta bibliografia/
cp tu_bibliografia.pdf bibliografia/

# Procesar nueva bibliografía
python main.py --process-docs
```

## 📖 Uso del Sistema

### Configuración Inicial

1. **Editar `config/indice.txt`** - Estructura de tu marco teórico:
```
2.1 Fundamentos Teóricos
2.1.1 Definiciones Conceptuales
2.1.2 Modelos Explicativos
2.2 Variables de Estudio
2.2.1 Variable Dependiente
2.2.2 Variables Independientes
```

2. **Modificar `config.py`** - Variables independientes de tu investigación:
```python
VARIABLES_INDEPENDIENTES = [
    "Tu variable 1",
    "Tu variable 2", 
    "Tu variable 3"
]
```

### Comandos Principales

#### Sistema Principal
```bash
# Inicializar y verificar sistema
python main.py

# Mostrar estadísticas
python main.py --stats

# Procesar nueva bibliografía
python main.py --process-docs

# Limpiar contextos previos
python main.py --clear-context

# Limpieza completa
python main.py --clean-all
```

#### Generación por Secciones
```bash
# Generar sección específica
python generar.py section 2.1

# Generar subsección específica
python generar.py section 2.1.1

# Listar secciones disponibles
python generar.py list

# Ver estado de la base de datos
python generar.py status

# Forzar reprocesamiento
python generar.py section 2.1 --force-reprocess
```

### Ejemplos de Uso

#### Generación Completa de Sección
```bash
# Genera sección 2.1 y todas sus subsecciones
python generar.py section 2.1
```

#### Generación Específica
```bash
# Genera solo la subsección 2.1.1
python generar.py section 2.1.1
```

## ⚙️ Configuración Avanzada

### Configuración de Agentes (`config.py`)

```python
AGENT_CONFIG = {
    "investigador": {
        "temperature": 0.2,      # Precisión en análisis
        "max_tokens": 4096       # Tokens para análisis profundo
    },
    "editor_fondo": {
        "temperature": 0.4,      # Creatividad controlada
        "max_tokens": 4096       # Contenido extenso con Gemma2
    },
    "redactor_forma": {
        "temperature": 0.3,      # Consistencia en formato
        "max_tokens": 4096       # Redacción extensa
    },
    "supervisor": {
        "temperature": 0.2,      # Rigor en revisión
        "max_tokens": 4096       # Revisiones detalladas
    }
}

# Configuración actual del modelo
OLLAMA_CONFIG = {
    "model": "gemma2:27b",      # Modelo de alta calidad
    "temperature": 0.3,
    "max_tokens": 4096
}
```

### Configuración RAG

```python
CHROMA_CONFIG = {
    "persist_directory": "./data/processed/chroma_db",
    "collection_name": "bibliografia_collection"
}
```

## 📊 Monitoreo y Estadísticas

### Ver Estado del Sistema
```bash
python main.py --stats
```

**Salida:**
```
📊 Estadísticas del Sistema
========================================
📚 Base de datos vectorial:
  - Total documentos: 9,780
  - Colección: bibliografia_collection

📄 Progreso del documento:
  - Total secciones: 12
  - Completadas: 8
  - Pendientes: 4
```

### Ver Archivos Generados
```bash
python generar.py status
```

## 🛠️ Resolución de Problemas

### Ollama No Responde
```bash
# Verificar estado de Ollama y modelos disponibles
ollama list

# Verificar que Gemma2 27B esté instalado
ollama run gemma2:27b "Test de funcionamiento"

# Reiniciar servidor si es necesario
pkill ollama
ollama serve
```

### Base de Datos Corrupta
```bash
# Limpiar y reconstruir
python main.py --clean-all
python main.py --process-docs
```

### Contenido de Baja Calidad
```bash
# Regenerar con reprocesamiento forzado
python generar.py section 2.1 --force-reprocess
```

## 📝 Personalización

### Personalización

### Variables de Investigación

El sistema es **completamente generalizable** para cualquier tema de investigación. Modifica `VARIABLES_INDEPENDIENTES` en `config.py`:

```python
# Para cualquier tema de investigación
VARIABLES_INDEPENDIENTES = [
    "Tu variable principal",
    "Tu variable contextual",
    "Tu variable de proceso",
    "Factores moderadores específicos",
    "Factores mediadores específicos"
]
```

**Ejemplos por disciplina:**

```python
# Tecnología Educativa
VARIABLES_INDEPENDIENTES = [
    "Tecnologías emergentes en educación",
    "Competencias digitales docentes", 
    "Engagement estudiantil digital",
    "Metodologías pedagógicas innovadoras",
    "Resultados de aprendizaje"
]

# Gestión Organizacional  
VARIABLES_INDEPENDIENTES = [
    "Liderazgo transformacional",
    "Cultura organizacional",
    "Clima laboral", 
    "Performance organizacional",
    "Factores de cambio organizacional"
]

# Psicología/Salud Mental
VARIABLES_INDEPENDIENTES = [
    "Burnout académico",
    "Estrés académico",
    "Salud mental universitaria", 
    "Factores individuales y conductuales",
    "Rendimiento y bienestar estudiantil"
]
```

### Estructura del Marco Teórico

Edita `config/indice.txt`:
```
2.1 Marco Conceptual
2.1.1 Definiciones Básicas
2.1.2 Teorías Fundamentales
2.2 Antecedentes Empíricos
2.2.1 Estudios Nacionales
2.2.2 Estudios Internacionales
```

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu característica (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 🏆 Créditos

Desarrollado para la automatización de marcos teóricos académicos de alta calidad utilizando tecnologías de IA avanzada.

## 📞 Soporte

Para soporte técnico o preguntas:
- Crear un Issue en GitHub
- Consultar la documentación en `config/README.md`
- Revisar logs en caso de errores

---

**⚡ Sistema en constante mejora - Contribuciones bienvenidas**
- **Iteración**: Puedes ajustar la configuración y regenerar el marco teórico
