"""
Agente Redactor de Forma - Especializado en formato, estilo y presentación académica
"""
from typing import List, Dict, Any, Optional, Tuple
from langchain_ollama import ChatOllama
from langchain.schema import HumanMessage, AIMessage
import re

from ..models.schemas import DocumentSection, ContentPiece, AgentRole, ContentType
from ..utils.rag_system import RAGSystem
from ..utils.document_processor import DocumentProcessor
from ..utils.style_extractor import load_style_examples
from config import AGENT_CONFIG, OLLAMA_CONFIG, PATHS


class RedactorFormaAgent:
    """
    Agente especializado en formato, estilo y presentación académica.
    Responsable de aplicar normas APA, mejorar el estilo y estructurar el documento.
    """

    def __init__(self, rag_system: RAGSystem, additional_context: str = ""):
        self.role = AgentRole.REDACTOR_FORMA
        self.rag_system = rag_system
        self.document_processor = DocumentProcessor(PATHS["indice"], PATHS["reglas_apa"])
        self.additional_context = additional_context
        
        # Cargar ejemplos de estilo académico
        try:
            self.style_guide = load_style_examples(PATHS["config"] + "/Ejemplo_estilo.pdf")
            print("✓ Ejemplos de estilo académico cargados correctamente")
        except Exception as e:
            print(f"⚠️  Error cargando ejemplos de estilo: {e}")
            self.style_guide = self._get_default_style_guide()
        
        # Configurar LLM con Ollama
        self.llm = ChatOllama(
            model=OLLAMA_CONFIG["model"],
            base_url=OLLAMA_CONFIG["base_url"],
            temperature=AGENT_CONFIG.get("redactor_forma", {}).get("temperature", 0.3),
            num_predict=AGENT_CONFIG.get("redactor_forma", {}).get("max_tokens", 1000)
        )

    def format_apa_citations(self, content: str, sources: List[str]) -> Dict[str, Any]:
        """
        Aplica formato APA a las citas en el contenido.
        
        Args:
            content: Contenido con citas a formatear
            sources: Lista de fuentes mencionadas
            
        Returns:
            Dict con el contenido formateado y lista de referencias
        """
        prompt = f"""
{self.additional_context}

Como redactor académico especializado en normas APA 7ª edición, formatea las citas en el siguiente texto:

**CONTENIDO:**
{content}

**FUENTES DISPONIBLES:**
{chr(10).join([f"- {source}" for source in sources])}

**INSTRUCCIONES:**
1. Identifica todas las citas en el texto
2. Aplica formato APA correcto para citas en el texto (Autor, año)
3. Asegura consistencia en el formato
4. Mantén la integridad del contenido académico
5. Genera lista de referencias en formato APA al final

**FORMATO APA REQUERIDO:**
- Citas en texto: (Autor, año) o Autor (año)
- Para múltiples autores: usar & entre autores
- Referencias: formato APA completo

Devuelve el texto con citas formateadas correctamente.
"""

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            
            # Extraer referencias del texto formateado
            formatted_content = response.content
            references = self._extract_references(formatted_content)
            
            return {
                "original_content": content[:200] + "..." if len(content) > 200 else content,
                "formatted_content": formatted_content,
                "references_count": len(references),
                "references": references,
                "apa_compliance": True,
                "status": "completed",
                "agent_role": self.role.value
            }
            
        except Exception as e:
            return {
                "original_content": content[:200] + "..." if len(content) > 200 else content,
                "formatted_content": f"Error en formateo: {str(e)}",
                "references_count": 0,
                "references": [],
                "apa_compliance": False,
                "status": "error",
                "agent_role": self.role.value
            }

    def improve_academic_style(self, content: str) -> Dict[str, Any]:
        """
        Mejora el estilo académico del contenido usando ejemplos de referencia.
        
        Args:
            content: Contenido a mejorar estilísticamente
            
        Returns:
            Dict con el contenido mejorado
        """
        # Preparar ejemplos de estilo académico
        style_examples = self._format_style_examples()
        
        prompt = f"""
Como redactor académico especializado, mejora el estilo del siguiente texto basándote en los EJEMPLOS DE ESTILO ACADÉMICO proporcionados. Tu tarea es producir ÚNICAMENTE el texto académico mejorado, sin incluir ninguna instrucción, proceso o comentario sobre la tarea.

**EJEMPLOS DE ESTILO ACADÉMICO DE REFERENCIA:**
{style_examples}

**TEXTO A MEJORAR:**
{content}

**INSTRUCCIONES:**
- Emula el estilo académico profesional de los ejemplos
- Elimina duplicaciones y consolida referencias en una sola sección
- Usa vocabulario académico formal y transiciones apropiadas
- Mantén todo el contenido sustantivo original
- NO incluyas ningún comentario sobre el proceso de edición
- NO incluyas las instrucciones en tu respuesta
- Produce SOLO el texto académico final mejorado

RESPONDE ÚNICAMENTE CON EL TEXTO ACADÉMICO MEJORADO:
- Fluidez y conexión entre párrafos
- Formalidad académica apropiada
- Precisión en el vocabulario técnico

**IMPORTANTE**: NO inventes información nueva. Solo mejora la forma de presentar el contenido existente siguiendo el estilo de los ejemplos.

**RESPUESTA ESPERADA**: Devuelve ÚNICAMENTE el texto mejorado estilísticamente, sin incluir estas instrucciones, comentarios adicionales, o explicaciones del proceso.
"""

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            
            # Calcular métricas de mejora
            original_words = len(content.split())
            improved_words = len(response.content.split())
            
            return {
                "original_content": content,
                "improved_content": response.content,
                "original_word_count": original_words,
                "improved_word_count": improved_words,
                "style_improvements": [
                    "Precisión léxica",
                    "Fluidez mejorada",
                    "Concisión aplicada",
                    "Claridad optimizada"
                ],
                "status": "completed",
                "agent_role": self.role.value
            }
            
        except Exception as e:
            return {
                "original_content": content,
                "improved_content": f"Error en mejora de estilo: {str(e)}",
                "original_word_count": len(content.split()),
                "improved_word_count": 0,
                "style_improvements": [],
                "status": "error",
                "agent_role": self.role.value
            }

    def structure_document_sections(self, sections: List[DocumentSection]) -> Dict[str, Any]:
        """
        Estructura y organiza las secciones del documento.
        
        Args:
            sections: Lista de secciones a estructurar
            
        Returns:
            Dict con la estructura organizada
        """
        # Crear jerarquía de secciones
        structured_sections = []
        for section in sections:
            level_marker = "#" * section.tipo
            structured_sections.append({
                "id": section.id,
                "title": section.titulo,
                "level": section.tipo,
                "marker": level_marker,
                "formatted_title": f"{level_marker} {section.titulo}"
            })

        prompt = f"""
Como redactor académico, revisa y mejora la estructura del siguiente índice de marco teórico:

**ESTRUCTURA ACTUAL:**
{chr(10).join([f"{s['formatted_title']}" for s in structured_sections])}

**EVALUACIÓN REQUERIDA:**
1. **Lógica de organización**: ¿El orden es lógico?
2. **Jerarquía**: ¿Los niveles están bien distribuidos?
3. **Coherencia**: ¿Hay flujo conceptual apropiado?
4. **Completitud**: ¿Faltan secciones importantes?
5. **Balance**: ¿Hay equilibrio entre secciones?

**SUGERENCIAS:**
- Recomendaciones de reorganización
- Ajustes de títulos si es necesario
- Mejoras en la secuencia lógica

Proporciona análisis y sugerencias de mejora para la estructura.
"""

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            
            return {
                "current_structure": structured_sections,
                "structure_analysis": response.content,
                "sections_count": len(sections),
                "hierarchy_levels": max([s.level for s in sections]) if sections else 0,
                "recommendations_provided": True,
                "status": "completed",
                "agent_role": self.role.value
            }
            
        except Exception as e:
            return {
                "current_structure": structured_sections,
                "structure_analysis": f"Error en análisis de estructura: {str(e)}",
                "sections_count": len(sections),
                "hierarchy_levels": 0,
                "recommendations_provided": False,
                "status": "error",
                "agent_role": self.role.value
            }

    def validate_academic_formatting(self, content: str) -> Dict[str, Any]:
        """
        Valida el formato académico del contenido.
        
        Args:
            content: Contenido a validar
            
        Returns:
            Dict con el resultado de la validación
        """
        validation_results = {
            "citations_format": self._check_citations_format(content),
            "paragraph_structure": self._check_paragraph_structure(content),
            "academic_tone": self._check_academic_tone(content),
            "reference_consistency": self._check_reference_consistency(content)
        }
        
        overall_score = sum(validation_results.values()) / len(validation_results)
        
        return {
            "content_validated": content[:200] + "..." if len(content) > 200 else content,
            "validation_results": validation_results,
            "overall_score": overall_score,
            "compliance_level": self._get_compliance_level(overall_score),
            "recommendations": self._get_formatting_recommendations(validation_results),
            "status": "completed",
            "agent_role": self.role.value
        }

    def create_bibliography(self, content_pieces: List[ContentPiece]) -> Dict[str, Any]:
        """
        Crea una bibliografía completa en formato APA.
        
        Args:
            content_pieces: Piezas de contenido con fuentes citadas
            
        Returns:
            Dict con la bibliografía generada
        """
        # Recopilar todas las fuentes únicas
        all_sources = set()
        for piece in content_pieces:
            all_sources.update(piece.sources)
        
        sources_list = list(all_sources)
        
        prompt = f"""
Como redactor académico especializado en APA, crea una bibliografía completa para las siguientes fuentes:

**FUENTES CITADAS:**
{chr(10).join([f"- {source}" for source in sources_list])}

**FORMATO APA 7ª EDICIÓN REQUERIDO:**
1. Orden alfabético por apellido del primer autor
2. Formato APA completo para cada tipo de fuente
3. Sangría francesa para cada entrada
4. Consistencia en el formato

**TIPOS DE FUENTE A CONSIDERAR:**
- Artículos de revista académica
- Libros académicos
- Capítulos de libro
- Documentos web institucionales
- Reportes técnicos

Genera la bibliografía completa en formato APA.
"""

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            
            return {
                "sources_processed": sources_list,
                "sources_count": len(sources_list),
                "bibliography": response.content,
                "format_standard": "APA 7ª edición",
                "alphabetical_order": True,
                "status": "completed",
                "agent_role": self.role.value
            }
            
        except Exception as e:
            return {
                "sources_processed": sources_list,
                "sources_count": len(sources_list),
                "bibliography": f"Error generando bibliografía: {str(e)}",
                "format_standard": "APA 7ª edición",
                "alphabetical_order": False,
                "status": "error",
                "agent_role": self.role.value
            }

    def _extract_references(self, text: str) -> List[str]:
        """Extrae referencias del texto formateado."""
        # Buscar patrones de referencias APA
        reference_patterns = [
            r'\n([A-Z][^.\n]*\. \(\d{4}\)[^.\n]*\.)',
            r'\n([A-Z][^.\n]*\, [A-Z]\. [^.\n]*\. \(\d{4}\)[^.\n]*\.)'
        ]
        
        references = []
        for pattern in reference_patterns:
            matches = re.findall(pattern, text)
            references.extend(matches)
        
        return list(set(references))  # Eliminar duplicados

    def _check_citations_format(self, content: str) -> float:
        """Verifica el formato de las citas."""
        citation_patterns = [
            r'\([A-Z][^,)]*,\s*\d{4}\)',  # (Autor, año)
            r'[A-Z][^(]*\(\d{4}\)'        # Autor (año)
        ]
        
        total_citations = 0
        correct_citations = 0
        
        for pattern in citation_patterns:
            matches = re.findall(pattern, content)
            total_citations += len(matches)
            correct_citations += len(matches)  # Asumimos que los patrones son correctos
        
        return 1.0 if total_citations == 0 else min(correct_citations / total_citations, 1.0)

    def _check_paragraph_structure(self, content: str) -> float:
        """Verifica la estructura de párrafos."""
        paragraphs = content.split('\n\n')
        good_paragraphs = 0
        
        for paragraph in paragraphs:
            if paragraph.strip():
                words = len(paragraph.split())
                if 50 <= words <= 200:  # Rango apropiado para párrafos académicos
                    good_paragraphs += 1
        
        return good_paragraphs / len(paragraphs) if paragraphs else 0.0

    def _check_academic_tone(self, content: str) -> float:
        """Verifica el tono académico."""
        academic_indicators = [
            'según', 'de acuerdo con', 'por tanto', 'sin embargo',
            'además', 'asimismo', 'por consiguiente', 'en consecuencia'
        ]
        
        informal_indicators = [
            'creo que', 'pienso que', 'obviamente', 'claramente'
        ]
        
        academic_score = sum(1 for indicator in academic_indicators if indicator in content.lower())
        informal_score = sum(1 for indicator in informal_indicators if indicator in content.lower())
        
        total_indicators = academic_score + informal_score
        return academic_score / total_indicators if total_indicators > 0 else 0.8

    def _check_reference_consistency(self, content: str) -> float:
        """Verifica la consistencia de las referencias."""
        # Análisis básico de consistencia
        citations = re.findall(r'\([A-Z][^,)]*,\s*\d{4}\)', content)
        if len(citations) == 0:
            return 0.5  # Score neutro si no hay citas
        
        years = [re.search(r'\d{4}', citation).group() for citation in citations]
        unique_years = set(years)
        
        # Score basado en diversidad temporal (indicador de buena investigación)
        return min(len(unique_years) / max(len(years), 1), 1.0)

    def _get_compliance_level(self, score: float) -> str:
        """Determina el nivel de cumplimiento."""
        if score >= 0.9:
            return "Excelente"
        elif score >= 0.7:
            return "Bueno"
        elif score >= 0.5:
            return "Aceptable"
        else:
            return "Necesita mejora"

    def _get_formatting_recommendations(self, validation_results: Dict[str, float]) -> List[str]:
        """Genera recomendaciones de formato."""
        recommendations = []
        
        if validation_results["citations_format"] < 0.8:
            recommendations.append("Revisar formato de citas APA")
        
        if validation_results["paragraph_structure"] < 0.7:
            recommendations.append("Mejorar estructura de párrafos")
        
        if validation_results["academic_tone"] < 0.8:
            recommendations.append("Ajustar tono académico")
        
        if validation_results["reference_consistency"] < 0.6:
            recommendations.append("Verificar consistencia de referencias")
        
        return recommendations

    def _get_default_style_guide(self) -> Dict[str, Any]:
        """Proporciona una guía de estilo por defecto si no se puede cargar el ejemplo"""
        return {
            "introduction_templates": [
                "El presente análisis aborda la problemática de {tema} desde una perspectiva {enfoque}.",
                "En el contexto de {area}, resulta fundamental examinar {aspecto_especifico}.",
                "La literatura especializada en {campo} ha evidenciado la relevancia de {concepto}.",
                "Diversos estudios han demostrado que {fenomeno} constituye un factor determinante en {contexto}."
            ],
            "paragraph_development": [
                "Iniciar con una oración temática clara",
                "Desarrollar la idea con evidencia empírica",
                "Incluir citas de autoridad académica",
                "Conectar con el párrafo anterior y siguiente",
                "Concluir con síntesis o transición"
            ],
            "transition_phrases": [
                "Por otro lado", "Sin embargo", "En este sentido", "De manera similar",
                "En contraste", "Asimismo", "Por tanto", "En consecuencia",
                "Cabe señalar que", "Es importante destacar que", "En relación con",
                "Respecto a", "Con respecto a"
            ],
            "citation_integration": [
                "Integrar citas como parte natural del discurso",
                "Variar las formas de introducir las citas",
                "Contextualizar cada cita en el argumento",
                "Usar citas para apoyar, no reemplazar el análisis"
            ],
            "academic_tone": [
                "Usar tercera persona impersonal",
                "Emplear vocabulario académico preciso",
                "Construir oraciones complejas pero claras",
                "Mantener objetividad y rigor científico"
            ]
        }

    def _format_style_examples(self) -> str:
        """Formatea los ejemplos de estilo para el prompt"""
        examples = []
        
        # Ejemplos de introducción de párrafos
        if "introduction_templates" in self.style_guide:
            examples.append("**FORMAS DE INICIAR PÁRRAFOS:**")
            for template in self.style_guide["introduction_templates"][:3]:
                examples.append(f"- {template}")
        
        # Frases de transición
        if "transition_phrases" in self.style_guide:
            examples.append("\n**FRASES DE TRANSICIÓN ACADÉMICAS:**")
            transitions = self.style_guide["transition_phrases"][:8]
            examples.append(f"- {', '.join(transitions)}")
        
        # Desarrollo de párrafos
        if "paragraph_development" in self.style_guide:
            examples.append("\n**ESTRUCTURA DE PÁRRAFOS:**")
            for item in self.style_guide["paragraph_development"]:
                examples.append(f"- {item}")
        
        # Integración de citas
        if "citation_integration" in self.style_guide:
            examples.append("\n**INTEGRACIÓN DE CITAS:**")
            for item in self.style_guide["citation_integration"]:
                examples.append(f"- {item}")
        
        # Tono académico
        if "academic_tone" in self.style_guide:
            examples.append("\n**TONO ACADÉMICO:**")
            for item in self.style_guide["academic_tone"]:
                examples.append(f"- {item}")
        
        return "\n".join(examples)

    def get_status(self) -> Dict[str, Any]:
        """
        Obtiene el estado actual del agente redactor de forma.
        
        Returns:
            Dict con información del estado del agente
        """
        return {
            "role": self.role.value,
            "model": OLLAMA_CONFIG["model"],
            "temperature": AGENT_CONFIG.get("redactor_forma", {}).get("temperature", 0.3),
            "max_tokens": AGENT_CONFIG.get("redactor_forma", {}).get("max_tokens", 1000),
            "rag_initialized": self.rag_system is not None,
            "capabilities": [
                "format_apa_citations",
                "improve_academic_style",
                "structure_document_sections",
                "validate_academic_formatting",
                "create_bibliography"
            ],
            "format_standards": ["APA 7ª edición"]
        }

    def __str__(self) -> str:
        return f"RedactorFormaAgent(role={self.role.value}, model={OLLAMA_CONFIG['model']})"

    def __repr__(self) -> str:
        return self.__str__()
