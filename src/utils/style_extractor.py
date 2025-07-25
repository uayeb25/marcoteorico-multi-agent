"""
Extractor de estilo de redacción académica
Procesa el ejemplo de estilo para que el Redactor de forma lo use como referencia
"""
import re
from typing import List, Dict, Any
from pathlib import Path
from dataclasses import dataclass

try:
    import pypdf
    PDF_LIBRARY = 'pypdf'
except ImportError:
    try:
        import PyPDF2
        PDF_LIBRARY = 'PyPDF2'
    except ImportError:
        print("Warning: No PDF library available. Install pypdf or PyPDF2")
        PDF_LIBRARY = None

@dataclass
class StyleExample:
    """Ejemplo de estilo de redacción"""
    section_type: str
    content: str
    characteristics: List[str]
    transition_patterns: List[str]

class StyleExtractor:
    """Extrae patrones de estilo de redacción del documento ejemplo"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        self.raw_text = ""
        self.style_examples = []
        
    def extract_text_from_pdf(self) -> str:
        """Extrae texto del PDF ejemplo"""
        if PDF_LIBRARY is None:
            print("No hay biblioteca PDF disponible. Usando texto de muestra.")
            return self._get_sample_academic_text()
            
        try:
            with open(self.pdf_path, 'rb') as file:
                if PDF_LIBRARY == 'pypdf':
                    import pypdf
                    pdf_reader = pypdf.PdfReader(file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                elif PDF_LIBRARY == 'PyPDF2':
                    import PyPDF2
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                        
                self.raw_text = text
                return text
        except Exception as e:
            print(f"Error extrayendo texto del PDF: {e}")
            return self._get_sample_academic_text()
    
    def _get_sample_academic_text(self) -> str:
        """Texto de muestra con estilo académico para casos donde no se puede leer el PDF"""
        return """
        La investigación en el ámbito educativo ha evidenciado la complejidad inherente a los procesos de enseñanza-aprendizaje. 
        En este sentido, diversos autores han señalado la relevancia de considerar múltiples factores que influyen en el 
        rendimiento académico. Según López et al. (2020), la motivación constituye un elemento fundamental en el desarrollo 
        de competencias académicas.
        
        Por otro lado, es importante destacar que las metodologías tradicionales han mostrado limitaciones significativas 
        en contextos contemporáneos. Como indica Martínez (2019), la incorporación de tecnologías emergentes representa 
        una oportunidad para optimizar los procesos educativos. Sin embargo, dicha implementación requiere de un análisis 
        exhaustivo de las condiciones institucionales.
        
        En relación con lo anterior, resulta pertinente examinar las implicaciones teóricas y prácticas de estas 
        transformaciones. La literatura especializada sugiere que los cambios paradigmáticos en educación demandan 
        enfoques interdisciplinarios que permitan abordar la complejidad del fenómeno educativo desde múltiples perspectivas.
        
        Asimismo, cabe señalar que las investigaciones recientes han identificado patrones consistentes en la relación 
        entre variables pedagógicas y resultados de aprendizaje. En consecuencia, se hace evidente la necesidad de 
        desarrollar marcos teóricos que integren estos hallazgos de manera coherente y sistemática.
        
        Finalmente, el análisis de la evidencia empírica disponible confirma la pertinencia de adoptar aproximaciones 
        metodológicas que permitan capturar la dinámica compleja de los procesos educativos. De este modo, se establece 
        un fundamento sólido para futuras investigaciones en el área.
        """
    
    def analyze_writing_patterns(self) -> Dict[str, Any]:
        """Analiza patrones de escritura académica del ejemplo"""
        if not self.raw_text:
            self.extract_text_from_pdf()
        
        patterns = {
            "paragraph_starters": self._extract_paragraph_starters(),
            "transition_phrases": self._extract_transition_phrases(),
            "citation_patterns": self._extract_citation_patterns(),
            "academic_vocabulary": self._extract_academic_vocabulary(),
            "sentence_structures": self._extract_sentence_structures(),
            "argumentation_patterns": self._extract_argumentation_patterns()
        }
        
        return patterns
    
    def _extract_paragraph_starters(self) -> List[str]:
        """Extrae formas comunes de iniciar párrafos"""
        paragraphs = self.raw_text.split('\n\n')
        starters = []
        
        for paragraph in paragraphs:
            if len(paragraph.strip()) > 50:  # Párrafos sustanciales
                first_sentence = paragraph.strip().split('.')[0]
                if len(first_sentence) > 10:
                    starters.append(first_sentence[:100])
        
        return starters[:20]  # Los primeros 20 ejemplos
    
    def _extract_transition_phrases(self) -> List[str]:
        """Extrae frases de transición comunes"""
        transition_patterns = [
            r"Por otro lado,?",
            r"Sin embargo,?",
            r"En este sentido,?",
            r"De manera similar,?",
            r"En contraste,?",
            r"Asimismo,?",
            r"Por tanto,?",
            r"En consecuencia,?",
            r"Cabe señalar que",
            r"Es importante destacar que",
            r"En relación con",
            r"Respecto a",
            r"Con respecto a"
        ]
        
        transitions = []
        for pattern in transition_patterns:
            matches = re.findall(pattern, self.raw_text, re.IGNORECASE)
            transitions.extend(matches)
        
        return list(set(transitions))
    
    def _extract_citation_patterns(self) -> List[str]:
        """Extrae patrones de citación del ejemplo"""
        citation_patterns = [
            r"según [A-Za-z\s,]+\(\d{4}\)",
            r"[A-Za-z\s,]+\(\d{4}\)\s+sostiene",
            r"[A-Za-z\s,]+\(\d{4}\)\s+argumenta",
            r"[A-Za-z\s,]+\(\d{4}\)\s+señala",
            r"como indica [A-Za-z\s,]+\(\d{4}\)",
            r"tal como menciona [A-Za-z\s,]+\(\d{4}\)"
        ]
        
        citations = []
        for pattern in citation_patterns:
            matches = re.findall(pattern, self.raw_text, re.IGNORECASE)
            citations.extend(matches)
        
        return citations[:15]
    
    def _extract_academic_vocabulary(self) -> List[str]:
        """Extrae vocabulario académico característico"""
        academic_terms = [
            "fundamental", "esencial", "relevante", "significativo",
            "considerable", "sustancial", "notable", "evidente",
            "comprende", "implica", "sugiere", "demuestra",
            "establece", "determina", "evidencia", "confirma",
            "perspectiva", "enfoque", "aproximación", "marco teórico",
            "conceptualización", "dimensión", "componente", "aspecto"
        ]
        
        found_terms = []
        for term in academic_terms:
            if term.lower() in self.raw_text.lower():
                found_terms.append(term)
        
        return found_terms
    
    def _extract_sentence_structures(self) -> List[str]:
        """Extrae estructuras de oraciones complejas"""
        sentences = re.split(r'[.!?]+', self.raw_text)
        complex_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            # Buscar oraciones con subordinadas
            if (len(sentence) > 80 and 
                ('que' in sentence or 'cual' in sentence or 'donde' in sentence or
                 'cuando' in sentence or 'mientras' in sentence)):
                complex_sentences.append(sentence[:200])
        
        return complex_sentences[:10]
    
    def _extract_argumentation_patterns(self) -> List[str]:
        """Extrae patrones de argumentación"""
        argument_patterns = [
            r"[^.]*por una parte[^.]*\.",
            r"[^.]*por otro lado[^.]*\.",
            r"[^.]*en primer lugar[^.]*\.",
            r"[^.]*en segundo lugar[^.]*\.",
            r"[^.]*finalmente[^.]*\.",
            r"[^.]*en conclusión[^.]*\.",
            r"[^.]*de este modo[^.]*\.",
            r"[^.]*en síntesis[^.]*\."
        ]
        
        arguments = []
        for pattern in argument_patterns:
            matches = re.findall(pattern, self.raw_text, re.IGNORECASE | re.DOTALL)
            arguments.extend(matches)
        
        return arguments[:10]
    
    def generate_style_guide(self) -> Dict[str, Any]:
        """Genera una guía de estilo basada en el ejemplo"""
        patterns = self.analyze_writing_patterns()
        
        style_guide = {
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
            
            "transition_phrases": patterns["transition_phrases"],
            
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
            ],
            
            "conclusion_patterns": [
                "Síntesis de puntos principales",
                "Conexión con objetivos del marco teórico",
                "Identificación de vacíos o futuras líneas",
                "Relevancia para la investigación actual"
            ]
        }
        
        return style_guide

def load_style_examples(pdf_path: str) -> Dict[str, Any]:
    """Función principal para cargar ejemplos de estilo"""
    extractor = StyleExtractor(pdf_path)
    return extractor.generate_style_guide()
