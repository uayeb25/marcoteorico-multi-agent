"""
Procesador de documentos para manejar el índice y las reglas APA
"""
import os
from typing import List, Dict, Any, Optional
from ..models.schemas import DocumentSection

class DocumentProcessor:
    """Procesador para manejar la estructura del documento y reglas APA"""
    
    def __init__(self, indice_path: str, reglas_apa_path: str):
        self.indice_path = indice_path
        self.reglas_apa_path = reglas_apa_path
        self.sections: List[DocumentSection] = []
        self.apa_rules = ""
        
        self._load_structure()
        self._load_apa_rules()
    
    def _load_structure(self):
        """Carga y parsea la estructura del índice"""
        if not os.path.exists(self.indice_path):
            raise FileNotFoundError(f"Archivo de índice no encontrado: {self.indice_path}")
        
        with open(self.indice_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line_num, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Determinar nivel basado en el formato de numeración
            level = self._determine_level(line)
            section_id = f"section_{line_num + 1}"
            
            # Extraer título (parte después de la numeración)
            parts = line.split(' ', 1)
            title = parts[1] if len(parts) > 1 else line
            
            # Determinar parent_id basado en el nivel
            parent_id = self._find_parent_id(level)
            
            section = DocumentSection(
                id=section_id,
                title=title,
                level=level,
                parent_id=parent_id
            )
            
            self.sections.append(section)
    
    def _determine_level(self, line: str) -> int:
        """Determina el nivel jerárquico basado en la numeración"""
        # Extraer la numeración al inicio de la línea
        import re
        match = re.match(r'^(\d+(?:\.\d+)*)', line.strip())
        if match:
            numbering = match.group(1)
            level = numbering.count('.') + 1
            return level
        else:
            return 1  # por defecto
    
    def _find_parent_id(self, current_level: int) -> Optional[str]:
        """Encuentra el ID del padre basado en el nivel actual"""
        if current_level <= 1:
            return None
        
        # Buscar la última sección de nivel inferior
        for section in reversed(self.sections):
            if section.level == current_level - 1:
                return section.id
        
        return None
    
    def _load_apa_rules(self):
        """Carga las reglas de citación APA"""
        if not os.path.exists(self.reglas_apa_path):
            raise FileNotFoundError(f"Archivo de reglas APA no encontrado: {self.reglas_apa_path}")
        
        with open(self.reglas_apa_path, 'r', encoding='utf-8') as f:
            self.apa_rules = f.read()
    
    def get_sections(self) -> List[DocumentSection]:
        """Retorna todas las secciones del documento"""
        return self.sections
    
    def get_section_by_id(self, section_id: str) -> Optional[DocumentSection]:
        """Busca una sección por su ID"""
        for section in self.sections:
            if section.id == section_id:
                return section
        return None
    
    def get_sections_by_level(self, level: int) -> List[DocumentSection]:
        """Retorna secciones de un nivel específico"""
        return [section for section in self.sections if section.level == level]
    
    def get_child_sections(self, parent_id: str) -> List[DocumentSection]:
        """Retorna las secciones hijas de una sección padre"""
        return [section for section in self.sections if section.parent_id == parent_id]
    
    def get_apa_rules(self) -> str:
        """Retorna las reglas de citación APA"""
        return self.apa_rules
    
    def get_section_context(self, section_id: str) -> Dict[str, Any]:
        """Obtiene el contexto completo de una sección"""
        section = self.get_section_by_id(section_id)
        if not section:
            return {}
        
        # Obtener sección padre si existe
        parent = None
        if section.parent_id:
            parent = self.get_section_by_id(section.parent_id)
        
        # Obtener secciones hijas
        children = self.get_child_sections(section_id)
        
        # Obtener secciones hermanas (mismo nivel y mismo padre)
        siblings = []
        if section.parent_id:
            siblings = [s for s in self.get_child_sections(section.parent_id) if s.id != section_id]
        else:
            siblings = [s for s in self.get_sections_by_level(section.level) if s.id != section_id]
        
        return {
            "section": section,
            "parent": parent,
            "children": children,
            "siblings": siblings,
            "full_path": self._get_section_path(section_id)
        }
    
    def _get_section_path(self, section_id: str) -> List[str]:
        """Obtiene la ruta completa de una sección (títulos de ancestros)"""
        path = []
        current_section = self.get_section_by_id(section_id)
        
        while current_section:
            path.insert(0, current_section.title)
            if current_section.parent_id:
                current_section = self.get_section_by_id(current_section.parent_id)
            else:
                break
        
        return path
    
    def generate_markdown_structure(self) -> str:
        """Genera la estructura del documento en formato Markdown"""
        markdown = "# Marco Teórico\\n\\n"
        
        for section in self.sections:
            # Generar headers basados en el nivel
            header_level = "#" * (section.level + 1)
            markdown += f"{header_level} {section.title}\\n\\n"
            
            if section.content:
                markdown += f"{section.content}\\n\\n"
            else:
                markdown += "*[Contenido pendiente de generar]*\\n\\n"
        
        return markdown
    
    def update_section_content(self, section_id: str, content: str, sources: List[str] = None):
        """Actualiza el contenido de una sección"""
        section = self.get_section_by_id(section_id)
        if section:
            section.content = content
            if sources:
                section.sources.extend(sources)
    
    def get_progress_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del progreso del documento"""
        total_sections = len(self.sections)
        completed_sections = len([s for s in self.sections if s.content])
        
        return {
            "total_sections": total_sections,
            "completed_sections": completed_sections,
            "pending_sections": total_sections - completed_sections,
            "completion_percentage": (completed_sections / total_sections * 100) if total_sections > 0 else 0,
            "sections_by_level": {
                level: len(self.get_sections_by_level(level))
                for level in range(1, 4)
            }
        }
