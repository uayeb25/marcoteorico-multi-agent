"""
Configuración del sistema multiagente para marco teórico
"""
from typing import Dict, Any
import os

# Configuración del modelo Ollama
OLLAMA_CONFIG = {
    "model": "gemma2:27b",  # Modelo más potente para mejores resultados
    "base_url": "http://localhost:11434",
    "temperature": 0.3,
    "top_p": 0.9,
    "max_tokens": 4096,  # Aumentado para más contenido
}

# Configuración de ChromaDB
CHROMA_CONFIG = {
    "persist_directory": "./data/processed/chroma_db",
    "collection_name": "bibliografia_collection"
}

# Configuración de paths
PATHS = {
    "bibliografia": "./bibliografia",
    "indice": "./config/indice.txt",
    "reglas_apa": "./config/reglas_citas_apa.txt",
    "variables": "./config/variables.txt",
    "contexto": "./config/Contexto.txt",
    "config": "./config",
    "output": "./output",
    "data": "./data"
}

# Variables independientes de la problemática (configurables según el tema de investigación)
# NOTA: Personalizar estas variables según tu tema de investigación específico
VARIABLES_INDEPENDIENTES = [
    "Variable principal de estudio",
    "Variable contextual", 
    "Variable de proceso",
    "Factores moderadores",
    "Factores mediadores"
]

# Ejemplo para burnout académico (comentado para referencia):
# VARIABLES_INDEPENDIENTES = [
#     "Burnout académico",
#     "Estrés académico", 
#     "Salud mental universitaria",
#     "Factores individuales y conductuales",
#     "Rendimiento y bienestar estudiantil"
# ]

# Configuración de agentes
AGENT_CONFIG = {
    "investigador": {
        "role": "Investigador académico especializado",
        "expertise": "Análisis de bibliografía, identificación de variables independientes",
        "temperature": 0.2,
        "max_tokens": 4000  # Aumentado para análisis más profundo
    },
    "editor_fondo": {
        "role": "Editor de contenido académico",
        "expertise": "Generación de párrafos con fuentes, conexión con variables independientes",
        "temperature": 0.4,
        "max_tokens": 8000  # Significativamente aumentado para contenido extenso
    },
    "redactor_forma": {
        "role": "Redactor académico especializado en formato APA",
        "expertise": "Formato APA, estructura de documentos académicos",
        "temperature": 0.3,
        "max_tokens": 6000  # Aumentado para redacción extensa
    },
    "supervisor": {
        "role": "Supervisor de calidad académica",
        "expertise": "Coherencia narrativa, revisión de contenido académico",
        "temperature": 0.2,
        "max_tokens": 4000  # Aumentado para revisiones detalladas
    }
}

# Configuración del workflow
WORKFLOW_CONFIG = {
    "max_iterations": 3,
    "review_threshold": 0.8,
    "chunk_size": 1000,
    "overlap": 200,
    "enable_multiagent": True,
    "parallel_processing": False,
    "quality_threshold": 0.7,
    "max_retry_attempts": 2
}

# Función para cargar el contexto de la investigación
def cargar_contexto_investigacion():
    """Carga el contexto de la investigación desde el archivo de configuración"""
    contexto_path = "./config/contexto_investigacion.txt"
    try:
        with open(contexto_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return """
        Contexto por defecto: 
        Investigación sobre burnout académico en estudiantes universitarios.
        Enfoque en factores individuales y conductuales.
        """

# Cargar contexto automáticamente
CONTEXTO_INVESTIGACION = cargar_contexto_investigacion()

# Configuración para incluir contexto en prompts de agentes
INCLUIR_CONTEXTO_EN_PROMPTS = True
