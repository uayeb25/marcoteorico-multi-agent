"""
Sistema Multiagente para Marco Teórico
Archivo principal para ejecutar y probar el sistema
"""
import os
import sys
import shutil
from pathlib import Path

# Agregar el directorio src al path para importaciones
src_path = Path(__file__).parent / "src"
sys.path.append(str(src_path))

from src.utils.rag_system import RAGSystem
from src.utils.document_processor import DocumentProcessor
from src.agents.investigador import InvestigadorAgent
from config import PATHS, CHROMA_CONFIG

def main():
    """Función principal para ejecutar el sistema"""
    print("🤖 Iniciando Sistema Multiagente para Marco Teórico")
    print("=" * 60)
    
    # Verificar que Ollama esté ejecutándose
    print("🔍 Verificando Ollama...")
    try:
        import ollama
        models = ollama.list()
        print(f"✅ Ollama funcionando. Modelos disponibles: {len(models['models'])}")
    except Exception as e:
        print(f"❌ Error con Ollama: {e}")
        print("Por favor, asegúrate de que Ollama esté ejecutándose: `ollama serve`")
        return
    
    # Inicializar componentes
    print("\n🔧 Inicializando componentes...")
    
    # 1. Sistema RAG
    print("📚 Configurando sistema RAG...")
    rag_system = RAGSystem()
    
    # 2. Procesador de documentos
    print("📄 Cargando estructura del documento...")
    try:
        doc_processor = DocumentProcessor(
            indice_path=PATHS["indice"],
            reglas_apa_path=PATHS["reglas_apa"]
        )
        sections = doc_processor.get_sections()
        print(f"✅ Cargadas {len(sections)} secciones del índice")
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        return
    
    # 3. Procesar bibliografía
    print("\n📖 Procesando bibliografía...")
    if os.path.exists(PATHS["bibliografia"]):
        sources = rag_system.process_bibliography_folder(PATHS["bibliografia"])
        print(f"✅ Procesados {len(sources)} documentos")
        
        # Mostrar estadísticas
        stats = rag_system.get_collection_stats()
        print(f"📊 Total de chunks en base vectorial: {stats.get('total_documents', 0)}")
    else:
        print(f"⚠️  Carpeta de bibliografía no encontrada: {PATHS['bibliografia']}")
    
    # 4. Inicializar agente investigador
    print("\n🧠 Inicializando Agente Investigador...")
    investigador = InvestigadorAgent(rag_system)
    print("✅ Agente Investigador listo")
    
    # 5. Realizar análisis de prueba
    print("\n🔬 Realizando análisis de prueba...")
    if sections:
        first_section = sections[0]
        print(f"Analizando sección: '{first_section.title}'")
        
        try:
            analysis = investigador.analyze_section_requirements(first_section)
            print(f"✅ Análisis completado")
            print(f"📊 Variables relevantes: {analysis['relevant_variables']}")
            print(f"📚 Fuentes disponibles: {len(analysis['available_sources'])}")
            print(f"📄 Chunks de contenido: {len(analysis['content_chunks'])}")
            
            # Mostrar un fragmento del análisis
            if analysis['analysis']:
                print(f"\n📝 Fragmento del análisis:")
                print("-" * 40)
                print(analysis['analysis'][:300] + "...")
                print("-" * 40)
                
        except Exception as e:
            print(f"❌ Error en análisis: {e}")
    
    print("\n🎉 Sistema inicializado correctamente!")
    print("\nComandos disponibles:")
    print("- python main.py --analyze [section_id]: Analizar sección específica")
    print("- python main.py --process-docs: Procesar nueva bibliografía")
    print("- python main.py --stats: Mostrar estadísticas del sistema")
    print("- python main.py --clear-context: Limpiar contextos previos de BD")
    print("- python main.py --clear-outputs: Limpiar carpeta outputs")
    print("- python main.py --clean-all: Limpieza completa (BD + outputs)")

def show_stats():
    """Muestra estadísticas del sistema"""
    rag_system = RAGSystem()
    doc_processor = DocumentProcessor(PATHS["indice"], PATHS["reglas_apa"])
    
    print("📊 Estadísticas del Sistema")
    print("=" * 40)
    
    # Estadísticas de RAG
    rag_stats = rag_system.get_collection_stats()
    print(f"📚 Base de datos vectorial:")
    print(f"  - Total documentos: {rag_stats.get('total_documents', 0)}")
    print(f"  - Colección: {rag_stats.get('collection_name', 'N/A')}")
    
    # Estadísticas de documento
    doc_stats = doc_processor.get_progress_stats()
    print(f"\n📄 Progreso del documento:")
    print(f"  - Total secciones: {doc_stats['total_sections']}")
    print(f"  - Completadas: {doc_stats['completed_sections']}")
    print(f"  - Pendientes: {doc_stats['pending_sections']}")
    print(f"  - Progreso: {doc_stats['completion_percentage']:.1f}%")

def process_new_docs():
    """Procesa nueva bibliografía"""
    print("📖 Procesando nueva bibliografía...")
    rag_system = RAGSystem()
    
    if os.path.exists(PATHS["bibliografia"]):
        # Limpiar colección existente
        rag_system.clear_collection()
        print("🗑️  Colección limpiada")
        
        # Procesar documentos
        sources = rag_system.process_bibliography_folder(PATHS["bibliografia"])
        print(f"✅ Procesados {len(sources)} documentos")
        
        # Mostrar estadísticas
        stats = rag_system.get_collection_stats()
        print(f"📊 Total de chunks: {stats.get('total_documents', 0)}")
    else:
        print(f"❌ Carpeta no encontrada: {PATHS['bibliografia']}")

def clear_context_data():
    """Limpia contextos previos de la BD vectorial"""
    print("🧹 Limpiando contextos previos de la BD vectorial...")
    rag_system = RAGSystem()
    
    try:
        rag_system.clear_context_chunks()
        print("✅ Contextos previos eliminados de la BD vectorial")
        
        # Mostrar estadísticas después de la limpieza
        stats = rag_system.get_collection_stats()
        print(f"📊 Chunks restantes en BD: {stats.get('total_documents', 0)}")
        
    except Exception as e:
        print(f"❌ Error al limpiar contextos: {e}")

def clear_outputs_folder():
    """Limpia todos los archivos de la carpeta outputs"""
    outputs_path = Path("outputs")
    
    if not outputs_path.exists():
        print("📁 Carpeta outputs no existe")
        return
    
    print("🧹 Limpiando carpeta outputs...")
    
    try:
        file_count = 0
        for file_path in outputs_path.iterdir():
            if file_path.is_file():
                file_path.unlink()
                file_count += 1
            elif file_path.is_dir():
                shutil.rmtree(file_path)
                file_count += 1
        
        print(f"✅ Eliminados {file_count} elementos de la carpeta outputs")
        
    except Exception as e:
        print(f"❌ Error al limpiar outputs: {e}")

def clean_all_context():
    """Limpia tanto contextos de BD como archivos outputs"""
    print("🧹 Limpieza completa de contextos...")
    print("=" * 50)
    
    # Limpiar BD vectorial
    clear_context_data()
    print()
    
    # Limpiar carpeta outputs
    clear_outputs_folder()
    print()
    
    print("✅ Limpieza completa finalizada")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--stats":
            show_stats()
        elif sys.argv[1] == "--process-docs":
            process_new_docs()
        elif sys.argv[1] == "--clear-context":
            clear_context_data()
        elif sys.argv[1] == "--clear-outputs":
            clear_outputs_folder()
        elif sys.argv[1] == "--clean-all":
            clean_all_context()
        elif sys.argv[1] == "--analyze" and len(sys.argv) > 2:
            # Análisis específico de sección
            section_id = sys.argv[2]
            print(f"🔍 Analizando sección: {section_id}")
            # Implementar análisis específico aquí
        else:
            print("❌ Comando no reconocido")
            print("Comandos disponibles:")
            print("  --stats: Mostrar estadísticas")
            print("  --process-docs: Procesar nueva bibliografía")
            print("  --clear-context: Limpiar contextos previos de BD")
            print("  --clear-outputs: Limpiar carpeta outputs")
            print("  --clean-all: Limpieza completa (BD + outputs)")
            print("  --analyze [section_id]: Analizar sección específica")
    else:
        main()
