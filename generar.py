#!/usr/bin/env python3
"""
Sistema de Generación por Secciones
Genera secciones específicas del marco teórico usando el sistema multiagente
Uso: python generar.py section 2.1
"""

import os
import sys
import argparse
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional

# Agregar el directorio src al path para importaciones
src_path = Path(__file__).parent / "src"
sys.path.append(str(src_path))

from src.utils.rag_system import RAGSystem
from src.utils.document_processor import DocumentProcessor
from src.agents.investigador import InvestigadorAgent
from src.agents.editor_fondo import EditorFondoAgent
from src.agents.redactor_forma import RedactorFormaAgent
from src.agents.supervisor import SupervisorAgent
from src.workflow.multi_agent_workflow import MultiAgentWorkflow, WorkflowContext, WorkflowState
from src.models.schemas import DocumentSection, ContentType, ContentPiece, AgentRole
from config import PATHS, CHROMA_CONFIG, VARIABLES_INDEPENDIENTES, OLLAMA_CONFIG, CONTEXTO_INVESTIGACION, INCLUIR_CONTEXTO_EN_PROMPTS


class SectionExtractor:
    """Extrae secciones específicas del índice y determina su alcance"""
    
    def __init__(self, indice_path: str):
        self.indice_path = indice_path
        self.sections = self._load_sections()
    
    def _load_sections(self) -> List[Dict]:
        """Carga todas las secciones del índice"""
        sections = []
        with open(self.indice_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line_num, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # Determinar nivel de la sección basado en indentación y numeración
            level = self._determine_level(line)
            section_number = self._extract_section_number(line)
            title = self._extract_title(line)
            
            if section_number and title:
                sections.append({
                    'number': section_number,
                    'title': title,
                    'full_line': line,
                    'level': level,
                    'line_num': line_num
                })
        
        return sections
    
    def _determine_level(self, line: str) -> int:
        """Determina el nivel jerárquico de la sección"""
        # Contar puntos en la numeración
        match = re.match(r'^(\d+(?:\.\d+)*)', line.strip())
        if match:
            return match.group(1).count('.') + 1
        return 1
    
    def _extract_section_number(self, line: str) -> Optional[str]:
        """Extrae el número de sección"""
        match = re.match(r'^(\d+(?:\.\d+)*)', line.strip())
        return match.group(1) if match else None
    
    def _extract_title(self, line: str) -> Optional[str]:
        """Extrae el título de la sección"""
        match = re.match(r'^\d+(?:\.\d+)*\s+(.+)$', line.strip())
        return match.group(1).strip() if match else None
    
    def get_section_range(self, target_section: str) -> Tuple[List[Dict], str, str]:
        """
        Obtiene el rango de secciones que deben generarse para la sección objetivo
        
        Args:
            target_section: Número de sección objetivo (ej: "2.1")
            
        Returns:
            Tuple de (lista_secciones, numero_inicio, numero_fin)
        """
        target_level = target_section.count('.') + 1
        section_start_idx = None
        section_end_idx = None
        
        # Encontrar índice de inicio
        for i, section in enumerate(self.sections):
            if section['number'] == target_section:
                section_start_idx = i
                break
        
        if section_start_idx is None:
            raise ValueError(f"Sección {target_section} no encontrada en el índice")
        
        # Encontrar índice de fin (siguiente sección del mismo nivel o superior)
        for i in range(section_start_idx + 1, len(self.sections)):
            current_level = self.sections[i]['level']
            if current_level <= target_level:
                section_end_idx = i
                break
        
        # Si no se encuentra fin, incluir hasta el final
        if section_end_idx is None:
            section_end_idx = len(self.sections)
        
        selected_sections = self.sections[section_start_idx:section_end_idx]
        start_number = selected_sections[0]['number']
        end_number = selected_sections[-1]['number'] if len(selected_sections) > 1 else start_number
        
        return selected_sections, start_number, end_number
    
    def get_section_info(self, section_number: str) -> Optional[Dict]:
        """Obtiene información de una sección específica"""
        for section in self.sections:
            if section['number'] == section_number:
                return section
        return None


class SectionGenerator:
    """Generador de contenido para secciones específicas usando multiagentes"""
    
    def __init__(self):
        self.rag_system = RAGSystem(model_name=OLLAMA_CONFIG["model"])
        self.doc_processor = DocumentProcessor(PATHS["indice"], PATHS["reglas_apa"])
        
        # Preparar contexto adicional para los agentes si está habilitado
        additional_context = ""
        if INCLUIR_CONTEXTO_EN_PROMPTS:
            additional_context = f"\n\n# CONTEXTO DE LA INVESTIGACIÓN\n{CONTEXTO_INVESTIGACION}\n"
        
        # Inicializar agentes con contexto adicional
        self.investigador = InvestigadorAgent(self.rag_system, additional_context=additional_context)
        self.editor_fondo = EditorFondoAgent(self.rag_system, additional_context=additional_context)
        self.redactor_forma = RedactorFormaAgent(self.rag_system, additional_context=additional_context)
        self.supervisor = SupervisorAgent(self.rag_system, additional_context=additional_context)
        self.workflow = MultiAgentWorkflow(self.rag_system)
        self.output_dir = Path("outputs")
        self.output_dir.mkdir(exist_ok=True)
    
    def setup_system(self, force_reprocess=False):
        """Configura el sistema RAG con la bibliografía"""
        print("🔧 Configurando sistema...")
        
        # Verificar Ollama
        try:
            import ollama
            models = ollama.list()
            print(f"✅ Ollama funcionando. Modelos disponibles: {len(models['models'])}")
        except Exception as e:
            print(f"❌ Error con Ollama: {e}")
            return False
        
        # Verificar estado de la base de datos vectorial
        stats = self.rag_system.get_collection_stats()
        current_docs = stats.get('total_documents', 0)
        
        if current_docs > 0 and not force_reprocess:
            print(f"📊 Base de datos vectorial existente: {current_docs} chunks")
            print("✅ Usando base de datos Chroma existente")
            return True
        else:
            if force_reprocess and current_docs > 0:
                print("� Forzando reprocesamiento de bibliografía...")
                self.rag_system.clear_collection()
            elif current_docs == 0:
                print("�📚 Base de datos vectorial vacía, procesando bibliografía...")
            
            # Procesar bibliografía
            if os.path.exists(PATHS["bibliografia"]):
                sources = self.rag_system.process_bibliography_folder(PATHS["bibliografia"])
                print(f"✅ Procesados {len(sources)} documentos")
                
                stats = self.rag_system.get_collection_stats()
                print(f"📊 Total chunks en BD vectorial: {stats.get('total_documents', 0)}")
                return True
            else:
                print(f"❌ Carpeta de bibliografía no encontrada: {PATHS['bibliografia']}")
                return False
    
    def load_previous_content(self) -> str:
        """Carga contenido previamente generado para contexto (limitado y optimizado)"""
        context_content = ""
        
        # Buscar archivos .md en outputs ordenados por nombre (solo los más recientes)
        output_files = sorted(self.output_dir.glob("*.md"))
        
        # Limitar a máximo 3 archivos más recientes para evitar sobrecarga
        recent_files = output_files[-3:] if len(output_files) > 3 else output_files
        
        total_chars = 0
        max_context_chars = 15000  # Limitar contexto para no sobrecargar
        
        for file_path in recent_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Limitar el tamaño del contexto
                    if total_chars + len(content) > max_context_chars:
                        remaining_chars = max_context_chars - total_chars
                        if remaining_chars > 500:  # Solo agregar si queda espacio significativo
                            content = content[:remaining_chars] + "...[contenido truncado]"
                        else:
                            break
                    
                    context_content += f"\n\n--- Contenido de {file_path.name} ---\n"
                    context_content += content
                    total_chars += len(content)
                    
                    if total_chars >= max_context_chars:
                        break
                        
            except Exception as e:
                print(f"⚠️ Error leyendo {file_path}: {e}")
        
        if context_content:
            # Agregar contexto a la base vectorial (ahora limpia automáticamente los anteriores)
            print("📝 Agregando contexto previo a la BD vectorial...")
            try:
                self.rag_system.add_context_content(context_content)
                print("✅ Contexto agregado exitosamente")
            except Exception as e:
                print(f"⚠️ Error agregando contexto: {e}")
        else:
            print("ℹ️ No hay contexto previo para agregar")
        
        return context_content
    
    def generate_section_content(self, sections: List[Dict]) -> str:
        """Genera contenido para las secciones usando multiagentes"""
        all_content = []
        
        print(f"🤖 Generando contenido para {len(sections)} secciones...")
        
        for i, section_info in enumerate(sections):
            print(f"\n📝 Procesando sección {section_info['number']}: {section_info['title']}")
            
            # Crear objeto DocumentSection
            document_section = DocumentSection(
                id=f"section_{section_info['number'].replace('.', '_')}",
                title=f"{section_info['number']} {section_info['title']}",
                level=section_info['level'],
                content="",
                sources=[],
                variables_relacionadas=VARIABLES_INDEPENDIENTES
            )
            
            try:
                # Paso 1: Investigación
                print(f"  🔍 Investigando fuentes relevantes...")
                investigation_result = self.investigador.analyze_section_requirements(document_section)
                relevant_sources = investigation_result.get('available_sources', [])
                real_citations = investigation_result.get('real_citations', [])
                print(f"  ✅ Encontradas {len(relevant_sources)} fuentes relevantes")
                
                # Paso 2: Generación de contenido de fondo
                print(f"  ✍️ Generando contenido académico...")
                content_result = self.editor_fondo.generate_section_content(
                    document_section, 
                    relevant_sources,
                    real_citations=real_citations
                )
                
                raw_content = content_result.get('generated_content', '')
                print(f"  ✅ Generadas {content_result.get('word_count', 0)} palabras")
                
                # Paso 3: Redacción y formato
                print(f"  📝 Aplicando formato académico...")
                formatted_result = self.redactor_forma.improve_academic_style(raw_content)
                
                formatted_content = formatted_result.get('improved_content', raw_content)
                
                # Paso 4: Supervisión de calidad (crear ContentPiece para evaluación)
                print(f"  🔍 Validando calidad...")
                content_piece = ContentPiece(
                    id=f"content_{section_info['number'].replace('.', '_')}",
                    section_id=document_section.id,
                    content_type=ContentType.PARAGRAPH,
                    content=formatted_content,
                    sources=content_result.get('sources_used', []),
                    variables_independientes=content_result.get('variables_addressed', []),
                    created_by=AgentRole.EDITOR_FONDO
                )
                
                quality_check = self.supervisor.evaluate_content_quality(content_piece)
                
                quality_score = quality_check.get('overall_score', 0)
                print(f"  📊 Puntuación de calidad: {quality_score:.2f}")
                
                # Agregar contenido con metadatos
                section_content = f"\n\n## {section_info['number']} {section_info['title']}\n\n"
                section_content += formatted_content
                
                # Agregar información de calidad como comentario
                section_content += f"\n\n<!-- Calidad: {quality_score:.2f}, Palabras: {content_result.get('word_count', 0)}, Variables: {', '.join(content_result.get('variables_addressed', []))} -->\n"
                
                all_content.append(section_content)
                
            except Exception as e:
                print(f"  ❌ Error generando sección {section_info['number']}: {e}")
                error_content = f"\n\n## {section_info['number']} {section_info['title']}\n\n"
                error_content += f"Error en la generación: {str(e)}\n\n"
                all_content.append(error_content)
        
        return "".join(all_content)
    
    def save_output(self, content: str, section_number: str, sections_info: List[Dict]) -> str:
        """Guarda el contenido generado en un archivo"""
        # Crear nombre de archivo basado en la sección
        filename = f"{section_number.replace('.', '_')}.md"
        filepath = self.output_dir / filename
        
        # Crear encabezado del archivo
        header = f"""# Marco Teórico - Sección {section_number}

**Generado:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Secciones incluidas:** {', '.join([s['number'] for s in sections_info])}
**Variables independientes:** {', '.join(VARIABLES_INDEPENDIENTES)}

---

"""
        
        # Escribir archivo
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(header + content)
            print(f"✅ Contenido guardado en: {filepath}")
            return str(filepath)
        except Exception as e:
            print(f"❌ Error guardando archivo: {e}")
            return ""
    
    def generate_section(self, target_section: str, force_reprocess: bool = False) -> bool:
        """Función principal para generar una sección específica"""
        print(f"🚀 Iniciando generación de sección {target_section}")
        print("=" * 60)
        
        try:
            # 1. Configurar sistema
            if not self.setup_system(force_reprocess):
                return False
            
            # 2. Cargar contexto previo
            print("\n📖 Cargando contexto previo...")
            previous_content = self.load_previous_content()
            if previous_content:
                print(f"✅ Contexto cargado: {len(previous_content.split())} palabras")
            else:
                print("ℹ️ No hay contexto previo disponible")
            
            # 3. Extraer secciones objetivo
            print(f"\n🎯 Extrayendo secciones para {target_section}...")
            extractor = SectionExtractor(PATHS["indice"])
            sections, start_num, end_num = extractor.get_section_range(target_section)
            
            print(f"✅ Secciones a generar: {start_num} - {end_num}")
            for section in sections:
                print(f"  - {section['number']}: {section['title']}")
            
            # 4. Generar contenido
            print(f"\n🤖 Iniciando generación multiagente...")
            content = self.generate_section_content(sections)
            
            # 5. Guardar resultado
            print(f"\n💾 Guardando resultado...")
            output_file = self.save_output(content, target_section, sections)
            
            if output_file:
                print(f"\n🎉 ¡Generación completada exitosamente!")
                print(f"📁 Archivo generado: {output_file}")
                return True
            else:
                print(f"\n❌ Error guardando el resultado")
                return False
                
        except Exception as e:
            print(f"\n❌ Error en la generación: {e}")
            return False


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description="Generador de secciones del marco teórico",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python generar.py section 2.1    # Genera sección 2.1 y subsecciones
  python generar.py section 2.1.1  # Genera solo sección 2.1.1
  python generar.py section 2.2    # Genera sección 2.2 y subsecciones
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponibles')
    
    # Comando section
    section_parser = subparsers.add_parser('section', help='Genera una sección específica')
    section_parser.add_argument('number', help='Número de sección (ej: 2.1, 2.1.1)')
    section_parser.add_argument('--force-reprocess', action='store_true', 
                               help='Fuerza el reprocesamiento de la bibliografía')
    
    # Comando list
    list_parser = subparsers.add_parser('list', help='Lista todas las secciones disponibles')
    
    # Comando status
    status_parser = subparsers.add_parser('status', help='Muestra el estado de la base de datos vectorial')
    
    args = parser.parse_args()
    
    if args.command == 'section':
        if not args.number:
            print("❌ Error: Debe especificar el número de sección")
            return
        
        # Validar formato de sección
        if not re.match(r'^\d+(\.\d+)*$', args.number):
            print("❌ Error: Formato de sección inválido. Use formato como 2.1 o 2.1.1")
            return
        
        generator = SectionGenerator()
        success = generator.generate_section(args.number, args.force_reprocess)
        sys.exit(0 if success else 1)
    
    elif args.command == 'list':
        # Listar todas las secciones
        try:
            extractor = SectionExtractor(PATHS["indice"])
            print("📋 Secciones disponibles:")
            print("=" * 40)
            for section in extractor.sections:
                indent = "  " * (section['level'] - 1)
                print(f"{indent}{section['number']} {section['title']}")
        except Exception as e:
            print(f"❌ Error listando secciones: {e}")
    
    elif args.command == 'status':
        # Mostrar estado de la base de datos
        try:
            rag_system = RAGSystem(model_name=OLLAMA_CONFIG["model"])
            stats = rag_system.get_collection_stats()
            print("📊 Estado de la Base de Datos Vectorial:")
            print("=" * 45)
            print(f"📚 Total de chunks: {stats.get('total_documents', 0)}")
            print(f"🗂️  Colección: {stats.get('collection_name', 'N/A')}")
            print(f"📁 Directorio: {stats.get('persist_directory', 'N/A')}")
            
            # Mostrar archivos en outputs
            output_dir = Path("outputs")
            if output_dir.exists():
                output_files = list(output_dir.glob("*.md"))
                print(f"\n📄 Archivos generados: {len(output_files)}")
                for file in sorted(output_files):
                    size = file.stat().st_size
                    print(f"  - {file.name} ({size:,} bytes)")
            else:
                print("\n📄 No hay archivos generados")
                
        except Exception as e:
            print(f"❌ Error obteniendo estado: {e}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
