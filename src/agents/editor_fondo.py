"""
Agente Editor de Fondo - Especializado en generación de contenido académico sustantivo
"""
from typing import List, Dict, Any, Optional
from langchain_ollama import ChatOllama
from langchain.schema import HumanMessage, AIMessage

from ..models.schemas import DocumentSection, ContentPiece, AgentRole, ContentType
from ..utils.rag_system import RAGSystem
from ..utils.document_processor import DocumentProcessor
from config import AGENT_CONFIG, OLLAMA_CONFIG, PATHS, VARIABLES_INDEPENDIENTES


class EditorFondoAgent:
    """
    Agente especializado en generación de contenido académico sustantivo.
    Responsable de crear párrafos conectados con variables independientes y fuentes.
    """

    def __init__(self, rag_system: RAGSystem):
        self.role = AgentRole.EDITOR_FONDO
        self.rag_system = rag_system
        self.document_processor = DocumentProcessor(PATHS["indice"], PATHS["reglas_apa"])
from config import AGENT_CONFIG, OLLAMA_CONFIG, VARIABLES_INDEPENDIENTES


class EditorFondoAgent:
    """
    Agente especializado en generación de contenido académico sustantivo.
    Responsable de crear párrafos conectados con variables independientes y fuentes.
    """

    def __init__(self, rag_system: RAGSystem, additional_context: str = ""):
        self.role = AgentRole.EDITOR_FONDO
        self.rag_system = rag_system
        self.document_processor = DocumentProcessor(PATHS["indice"], PATHS["reglas_apa"])
        self.additional_context = additional_context
        
        # Configurar LLM con Ollama
        self.llm = ChatOllama(
            model=OLLAMA_CONFIG["model"],
            base_url=OLLAMA_CONFIG["base_url"],
            temperature=AGENT_CONFIG["editor_fondo"]["temperature"],
            num_predict=AGENT_CONFIG["editor_fondo"]["max_tokens"]
        )

    def generate_section_content(self, section: DocumentSection, relevant_sources: List[ContentPiece], real_citations: List[Dict] = None) -> Dict[str, Any]:
        """
        Genera contenido académico sustantivo para una sección específica.
        
        Args:
            section: Sección del documento a desarrollar
            relevant_sources: Fuentes relevantes encontradas por el investigador
            real_citations: Citas reales extraídas de los PDFs
            
        Returns:
            Dict con el contenido generado
        """
        if real_citations is None:
            real_citations = []
            
        # Preparar contexto de fuentes - USAR MÁS FUENTES PARA MAYOR VARIEDAD
        sources_context = "\n".join([
            f"Fuente {i+1}: {source.content[:500]}..." # Más contenido por fuente
            for i, source in enumerate(relevant_sources[:10])  # Usar hasta 10 fuentes
        ])
        
        # Preparar contexto de citas reales
        if real_citations:
            citations_context = "CITAS REALES AUTORIZADAS PARA USO:\n"
            for i, citation in enumerate(real_citations[:8]):  # Más citas disponibles
                citations_context += f"\n{i+1}. {citation['author']} ({citation['year']}). {citation['title']}. {citation.get('journal', '')} {citation.get('source', '')}"
            citations_context += "\n\n⚠️ USAR SOLO ESTAS CITAS - NO INVENTAR OTRAS"
        else:
            citations_context = "⚠️ NO HAY CITAS ESPECÍFICAS DISPONIBLES - BASAR CONTENIDO EN LAS FUENTES SIN INVENTAR REFERENCIAS"
        
        # Identificar variables independientes relevantes
        relevant_variables = [var for var in VARIABLES_INDEPENDIENTES 
                            if any(keyword in section.title.lower() 
                                  for keyword in var.lower().split())]
        
        prompt = f"""
{self.additional_context}

Como editor académico especializado, desarrolla contenido académico profundo y comprehensivo para la siguiente sección del marco teórico:

**SECCIÓN:** {section.title}
**NIVEL:** {section.level}
**VARIABLES INDEPENDIENTES RELEVANTES:** {', '.join(relevant_variables)}

**FUENTES DISPONIBLES:**
{sources_context}

**CITAS REALES DISPONIBLES (USAR ESTAS EN LUGAR DE CITAS FICTICIAS):**
{citations_context}

🚨 **REGLAS CRÍTICAS SOBRE CITAS - CUMPLIMIENTO OBLIGATORIO** 🚨

❌ **CITAS TOTALMENTE PROHIBIDAS (BLOQUEAR INMEDIATAMENTE):**
- Maslach & Jackson (1981) - PROHIBIDA
- Maslach, C., & Jackson, S. E. (1981) - PROHIBIDA 
- Demerouti & Bakker (2017) - PROHIBIDA
- OMS (2019) - PROHIBIDA
- WHO (2019) - PROHIBIDA
- Burnout Research Consortium - PROHIBIDA
- American Psychological Association - PROHIBIDA
- World Health Organization - PROHIBIDA
- Cualquier variación de Maslach - PROHIBIDA
- Cualquier cita académica que no esté explícitamente autorizada - PROHIBIDA

⚠️ **CONSECUENCIA DE USAR CITAS PROHIBIDAS**: El contenido será RECHAZADO

✅ **ÚNICAS CITAS AUTORIZADAS (VERIFICAR LISTA):**
{citations_context}

� **VERIFICACIÓN OBLIGATORIA ANTES DE CUALQUIER CITA:**
1. ¿Aparece EXACTAMENTE en la lista de citas autorizadas? → SI: Proceder. NO: ELIMINAR
2. ¿Es similar a una cita prohibida? → ELIMINAR inmediatamente
3. ¿Parece académicamente válida pero no está autorizada? → ELIMINAR

🎯 **SI NO HAY CITAS AUTORIZADAS**: Escribir contenido descriptivo SIN CITAS en lugar de inventar

🎯 **ENFOQUE TEMÁTICO ESPECÍFICO**: 
- El contenido DEBE centrarse ÚNICAMENTE en el tema específico de la sección: "{section.title}"
- NO generar contenido genérico sobre burnout académico
- NO usar numeración incorrecta (como 2.1.x cuando debería ser sobre el tema específico)
- Desarrollar ESPECÍFICAMENTE el aspecto mencionado en el título de la sección

**INSTRUCCIONES ESPECÍFICAS - CONTENIDO EXTENSO Y PROFUNDO:**
1. Genera contenido académico EXTENSO y DETALLADO de nivel universitario avanzado
2. MÍNIMO 800-1200 palabras por sección principal, 500-700 palabras por subsección
3. Usa TODAS las fuentes disponibles, no solo las primeras
4. Incluye múltiples perspectivas teóricas y enfoques metodológicos
5. Desarrolla argumentos complejos con análisis crítico profundo
6. NO repitas el título de la sección (viene automáticamente del sistema)

**ESTRUCTURA EXTENSIVA REQUERIDA:**
1. **Introducción conceptual** (2-3 párrafos, 200-300 palabras total)
2. **Desarrollo teórico principal** (4-5 párrafos, 200-250 palabras cada uno)
3. **Análisis metodológico y evidencia empírica** (2-3 párrafos, 150-200 palabras cada uno)
4. **Perspectivas comparativas y debates actuales** (2 párrafos, 150-200 palabras cada uno)
5. **Tabla comparativa compleja** (1 tabla detallada + 1 párrafo explicativo 150 palabras)
6. **Conexiones con variables independientes** (2 párrafos, 150-200 palabras cada uno)
7. **Implicaciones teóricas y prácticas** (1 párrafo, 150-200 palabras)
8. **Referencias** (al final, una sola vez, SOLO las citas reales utilizadas)

**FORMATO DE RESPUESTA EXTENSO (ESTRUCTURA FIJA - NO INCLUIR TÍTULO DE SECCIÓN):**

[Párrafo 1: Introducción conceptual - contexto teórico y definiciones fundamentales - 150 palabras]

[Párrafo 2: Marco conceptual complementario - perspectivas adicionales y enfoques disciplinarios - 150 palabras]

**Desarrollo teórico principal**

[Párrafo 1: Primera perspectiva teórica principal - 250 palabras con análisis profundo]

[Párrafo 2: Segunda perspectiva teórica - enfoques complementarios y contrastantes - 250 palabras]

[Párrafo 3: Tercera perspectiva - síntesis e integración teórica - 200 palabras]

[Párrafo 4: Evidencia empírica contemporánea - estudios recientes y hallazgos - 200 palabras]

**Análisis metodológico y evidencia empírica**

[Párrafo 1: Metodologías de investigación - enfoques cuantitativos y cualitativos - 180 palabras]

[Párrafo 2: Hallazgos empíricos clave - resultados de investigación y tendencias - 180 palabras]

**Perspectivas comparativas y debates actuales**

[Párrafo 1: Debates teóricos contemporáneos - controversias y discusiones académicas - 180 palabras]

[Párrafo 2: Comparación de enfoques - ventajas y limitaciones de diferentes perspectivas - 180 palabras]

**Tabla [Número]: [Título descriptivo y específico]**
| Aspecto | Perspectiva A | Perspectiva B | Perspectiva C | Implicaciones |
|---------|---------------|---------------|---------------|---------------|
| [Elemento 1] | [Descripción detallada] | [Descripción contrastante] | [Enfoque alternativo] | [Implicaciones teóricas] |
| [Elemento 2] | [Descripción detallada] | [Descripción contrastante] | [Enfoque alternativo] | [Implicaciones prácticas] |
| [Elemento 3] | [Descripción detallada] | [Descripción contrastante] | [Enfoque alternativo] | [Implicaciones metodológicas] |
| [Elemento 4] | [Descripción detallada] | [Descripción contrastante] | [Enfoque alternativo] | [Implicaciones futuras] |

[Párrafo explicativo de la tabla - análisis comparativo detallado - 150 palabras]

**Conexiones con variables independientes**

[Párrafo 1: Primera conexión - relación con variables específicas - 180 palabras]

[Párrafo 2: Segunda conexión - interacciones complejas y mediadores - 180 palabras]

**Implicaciones teóricas y prácticas**

[Párrafo síntesis - implicaciones para la teoría, investigación y práctica - 180 palabras]

[Párrafo explicativo de la tabla]

**Conexiones con variables independientes**

[Párrafo conectando específicamente con las variables de burnout académico]

**Referencias**

[Lista SOLO de las citas reales utilizadas del listado proporcionado - NO inventar ninguna nueva]

⚠️ CRÍTICO: El título de sección (## 2.1.1 Definición...) se agrega automáticamente - NO lo incluyas en tu respuesta.

[Párrafo introductorio con definiciones básicas]

[Párrafo de desarrollo conceptual principal]

### Tabla [Número]: [Título descriptivo]
| Aspecto | Descripción | Ejemplo |
|---------|-------------|---------|
| [Fila 1] | [Descripción] | [Ejemplo] |
| [Fila 2] | [Descripción] | [Ejemplo] |
| [Fila 3] | [Descripción] | [Ejemplo] |

[Párrafo conectando con variables independientes]

### Figura [Número]: [Título sugerido]
**Descripción:** [Descripción de figura/diagrama sugerido]
**Elementos:** [Lista de elementos que debería contener]

[Párrafo de síntesis y transición]

Asegúrate de que cada párrafo tenga al menos una cita y que las tablas sean informativas y relevantes.
"""

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            
            # Aplanar las listas de fuentes
            all_sources = []
            for source in relevant_sources:
                all_sources.extend(source.sources)
            
            return {
                "section_id": section.id,
                "section_title": section.title,
                "generated_content": response.content,
                "variables_addressed": relevant_variables,
                "sources_used": all_sources,
                "word_count": len(response.content.split()),
                "status": "completed",
                "agent_role": self.role.value
            }
            
        except Exception as e:
            return {
                "section_id": section.id,
                "section_title": section.title,
                "generated_content": f"Error en la generación: {str(e)}",
                "variables_addressed": relevant_variables,
                "sources_used": [],
                "word_count": 0,
                "status": "error",
                "agent_role": self.role.value
            }

    def enhance_paragraph(self, paragraph: str, variable_focus: str, additional_sources: List[str] = None) -> Dict[str, Any]:
        """
        Mejora un párrafo existente enfocándose en una variable independiente específica.
        
        Args:
            paragraph: Párrafo a mejorar
            variable_focus: Variable independiente a enfatizar
            additional_sources: Fuentes adicionales opcionales
            
        Returns:
            Dict con el párrafo mejorado
        """
        sources_text = ""
        if additional_sources:
            sources_text = f"\n**FUENTES ADICIONALES:**\n" + "\n".join(additional_sources)

        prompt = f"""
Como editor académico, mejora el siguiente párrafo enfocándote específicamente en la variable independiente indicada:

**PÁRRAFO ORIGINAL:**
{paragraph}

**VARIABLE INDEPENDIENTE A ENFATIZAR:** {variable_focus}
{sources_text}

**MEJORAS REQUERIDAS:**
1. Amplía la conexión con la variable independiente especificada
2. Agrega detalles conceptuales relevantes
3. Incluye ejemplos o aplicaciones específicas
4. Mejora la fluidez y coherencia
5. Mantén el rigor académico
6. Conserva o mejora las citas existentes

**RESULTADO:** Devuelve el párrafo mejorado manteniendo la estructura académica formal.
"""

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            
            return {
                "original_paragraph": paragraph[:200] + "..." if len(paragraph) > 200 else paragraph,
                "enhanced_paragraph": response.content,
                "variable_focus": variable_focus,
                "improvement_applied": True,
                "status": "completed",
                "agent_role": self.role.value
            }
            
        except Exception as e:
            return {
                "original_paragraph": paragraph[:200] + "..." if len(paragraph) > 200 else paragraph,
                "enhanced_paragraph": f"Error en la mejora: {str(e)}",
                "variable_focus": variable_focus,
                "improvement_applied": False,
                "status": "error",
                "agent_role": self.role.value
            }

    def create_transition_paragraph(self, current_section: str, next_section: str) -> Dict[str, Any]:
        """
        Crea un párrafo de transición entre secciones.
        
        Args:
            current_section: Sección actual
            next_section: Siguiente sección
            
        Returns:
            Dict con el párrafo de transición
        """
        prompt = f"""
Como editor académico, crea un párrafo de transición fluido y académico entre las siguientes secciones:

**SECCIÓN ACTUAL:** {current_section}
**SIGUIENTE SECCIÓN:** {next_section}

**CARACTERÍSTICAS DEL PÁRRAFO:**
1. 40-60 palabras máximo
2. Conecta lógicamente ambas secciones
3. Mantiene el hilo argumentativo
4. Usa conectores académicos apropiados
5. Prepara al lector para el cambio de tema

**FORMATO:** Un solo párrafo sin citas, enfocado en la transición conceptual.
"""

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            
            return {
                "from_section": current_section,
                "to_section": next_section,
                "transition_paragraph": response.content,
                "word_count": len(response.content.split()),
                "status": "completed",
                "agent_role": self.role.value
            }
            
        except Exception as e:
            return {
                "from_section": current_section,
                "to_section": next_section,
                "transition_paragraph": f"Error en la transición: {str(e)}",
                "word_count": 0,
                "status": "error",
                "agent_role": self.role.value
            }

    def synthesize_concepts(self, concepts: List[str], target_variable: str) -> Dict[str, Any]:
        """
        Sintetiza múltiples conceptos relacionados con una variable independiente.
        
        Args:
            concepts: Lista de conceptos a sintetizar
            target_variable: Variable independiente objetivo
            
        Returns:
            Dict con la síntesis conceptual
        """
        concepts_text = "\n".join([f"- {concept}" for concept in concepts])
        
        prompt = f"""
Como editor académico especializado, sintetiza los siguientes conceptos en relación con la variable independiente especificada:

**VARIABLE INDEPENDIENTE:** {target_variable}

**CONCEPTOS A SINTETIZAR:**
{concepts_text}

**INSTRUCCIONES:**
1. Identifica las relaciones entre los conceptos
2. Construye un marco conceptual coherente
3. Conecta todos los conceptos con la variable independiente
4. Crea una síntesis de 150-200 palabras
5. Usa lenguaje académico preciso
6. Estructura la síntesis lógicamente

**FORMATO:** Un párrafo sintético que integre todos los conceptos de manera coherente.
"""

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            
            return {
                "target_variable": target_variable,
                "concepts_synthesized": concepts,
                "synthesis": response.content,
                "concepts_count": len(concepts),
                "word_count": len(response.content.split()),
                "status": "completed",
                "agent_role": self.role.value
            }
            
        except Exception as e:
            return {
                "target_variable": target_variable,
                "concepts_synthesized": concepts,
                "synthesis": f"Error en la síntesis: {str(e)}",
                "concepts_count": len(concepts),
                "word_count": 0,
                "status": "error",
                "agent_role": self.role.value
            }

    def generate_content_piece(self, section_id: str, content_type: ContentType, requirements: Dict[str, Any]) -> ContentPiece:
        """
        Genera una pieza de contenido específica según los requerimientos.
        
        Args:
            section_id: ID de la sección
            content_type: Tipo de contenido a generar
            requirements: Requerimientos específicos
            
        Returns:
            ContentPiece: Pieza de contenido generada
        """
        try:
            if content_type == ContentType.PARAGRAPH:
                content = self.generate_section_content(
                    requirements.get("section"), 
                    requirements.get("sources", [])
                )
                generated_text = content["generated_content"]
                sources = content["sources_used"]
                variables = content["variables_addressed"]
                
            else:
                generated_text = f"Contenido de tipo {content_type.value} generado"
                sources = []
                variables = []
            
            content_piece = ContentPiece(
                id=f"editor_fondo_{section_id}_{content_type.value}",
                section_id=section_id,
                content_type=content_type,
                content=generated_text,
                sources=sources,
                variables_independientes=variables,
                created_by=self.role,
                quality_score=0.85  # Score base para contenido generado
            )
            
            return content_piece
            
        except Exception as e:
            # Crear contenido de error
            error_content = ContentPiece(
                id=f"editor_fondo_error_{section_id}",
                section_id=section_id,
                content_type=ContentType.PARAGRAPH,
                content=f"Error generando contenido: {str(e)}",
                sources=[],
                variables_independientes=[],
                created_by=self.role,
                quality_score=0.0
            )
            return error_content

    def generate_content_table(self, topic: str, relevant_sources: List[ContentPiece]) -> Dict[str, Any]:
        """
        Genera una tabla académica específica para un tema.
        
        Args:
            topic: Tema para la tabla
            relevant_sources: Fuentes relevantes
            
        Returns:
            Dict con la tabla generada
        """
        sources_context = "\n".join([
            f"Fuente {i+1}: {source.content[:200]}..."
            for i, source in enumerate(relevant_sources[:3])
        ])
        
        prompt = f"""
Como editor académico, crea una tabla informativa y bien estructurada sobre el siguiente tema:

**TEMA:** {topic}

**FUENTES DISPONIBLES:**
{sources_context}

**INSTRUCCIONES:**
1. Crea una tabla de 4-6 filas con 3-4 columnas
2. Incluye encabezados descriptivos y claros
3. Asegúrate de que la información sea precisa y relevante
4. Basate en las fuentes proporcionadas cuando sea posible
5. Usa formato Markdown para la tabla

**TIPOS DE TABLA SUGERIDOS:**
- Tabla comparativa (características vs. enfoques)
- Tabla de clasificación (categorías y ejemplos)
- Tabla de ventajas/desventajas
- Tabla de procesos (pasos y descripciones)

**FORMATO DE RESPUESTA:**
### Tabla: [Título descriptivo]

| [Columna 1] | [Columna 2] | [Columna 3] | [Columna 4] |
|-------------|-------------|-------------|-------------|
| [Dato 1] | [Dato 2] | [Dato 3] | [Dato 4] |
| [Dato 1] | [Dato 2] | [Dato 3] | [Dato 4] |
| [Dato 1] | [Dato 2] | [Dato 3] | [Dato 4] |

**Fuente:** Elaboración propia basada en [citar fuentes]

Genera una tabla útil e informativa que enriquezca el contenido académico.
"""

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            
            return {
                "topic": topic,
                "table_content": response.content,
                "status": "completed",
                "agent_role": self.role.value
            }
            
        except Exception as e:
            return {
                "topic": topic,
                "table_content": f"Error generando tabla: {str(e)}",
                "status": "error",
                "agent_role": self.role.value
            }

    def suggest_figure(self, topic: str, context: str) -> Dict[str, Any]:
        """
        Sugiere una figura o diagrama para enriquecer el contenido.
        
        Args:
            topic: Tema para la figura
            context: Contexto del contenido
            
        Returns:
            Dict con la sugerencia de figura
        """
        prompt = f"""
Como editor académico especializado, sugiere una figura o diagrama que enriquezca el siguiente contenido:

**TEMA:** {topic}
**CONTEXTO:** {context}

**INSTRUCCIONES:**
1. Sugiere un tipo de figura apropiado (diagrama, esquema, gráfico, etc.)
2. Proporciona un título descriptivo
3. Lista los elementos principales que debe contener
4. Explica cómo contribuiría al entendimiento del tema
5. Sugiere la posición óptima en el texto

**TIPOS DE FIGURA SUGERIDOS:**
- Diagrama de flujo (para procesos)
- Esquema conceptual (para relaciones)
- Gráfico comparativo (para datos)
- Modelo teórico (para frameworks)
- Timeline (para evolución temporal)

**FORMATO DE RESPUESTA:**
### Figura [Número]: [Título descriptivo]

**Tipo:** [Tipo de figura]
**Descripción:** [Descripción detallada de qué mostraría]
**Elementos principales:**
- [Elemento 1]
- [Elemento 2]
- [Elemento 3]

**Contribución:** [Cómo ayudaría al entendimiento]
**Posición sugerida:** [Dónde ubicarla en el texto]

Proporciona una sugerencia útil y específica.
"""

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            
            return {
                "topic": topic,
                "figure_suggestion": response.content,
                "status": "completed",
                "agent_role": self.role.value
            }
            
        except Exception as e:
            return {
                "topic": topic,
                "figure_suggestion": f"Error sugiriendo figura: {str(e)}",
                "status": "error",
                "agent_role": self.role.value
            }

    def generate_comprehensive_content(self, section, fuentes_disponibles, variables_independientes, modo="principal"):
        """
        Genera contenido académico extenso y detallado en diferentes modos.
        
        Args:
            section: Sección del documento
            fuentes_disponibles: Lista de fuentes disponibles
            variables_independientes: Variables del estudio
            modo: Tipo de contenido ("principal", "comparativo", "variables")
            
        Returns:
            Dict con contenido generado extenso
        """
        if modo == "principal":
            return self._generate_principal_content(section, fuentes_disponibles, variables_independientes)
        elif modo == "comparativo":
            return self._generate_comparative_content(section, fuentes_disponibles, variables_independientes)
        elif modo == "variables":
            return self._generate_variables_content(section, fuentes_disponibles, variables_independientes)
        else:
            return self.generate_section_content(section, fuentes_disponibles)

    def _generate_principal_content(self, section, fuentes_disponibles, variables_independientes):
        """Genera contenido principal extenso y detallado"""
        
        sources_context = "\n".join([
            f"Fuente {i+1}: {source.content[:400]}..."
            for i, source in enumerate(fuentes_disponibles[:8])  # Más fuentes
        ])
        
        prompt = f"""
Como editor académico especializado, desarrolla contenido PRINCIPAL extenso y detallado para:

**SECCIÓN:** {section.title}
**VARIABLES INDEPENDIENTES:** {', '.join(variables_independientes)}

**FUENTES DISPONIBLES:**
{sources_context}

**INSTRUCCIONES PARA CONTENIDO PRINCIPAL (1200-1500 palabras):**
1. Introducción conceptual completa con definiciones múltiples
2. Desarrollo histórico del concepto
3. Teorías fundamentales y enfoques principales
4. Estado actual de la investigación
5. Debates y controversias actuales
6. Múltiples perspectivas disciplinarias

**ESTRUCTURA OBLIGATORIA:**
- Párrafo introductorio (100-150 palabras)
- 4-5 párrafos de desarrollo teórico (150-200 palabras cada uno)
- 2-3 párrafos de análisis crítico
- Párrafo de síntesis
- Mínimo 8 citas académicas diferentes
- Al menos una tabla clasificatoria

GENERA CONTENIDO ACADÉMICO PRINCIPAL EXTENSO Y DETALLADO:
"""

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            return {
                "tipo": "principal",
                "contenido": response.content,
                "palabras": len(response.content.split()),
                "status": "completed"
            }
        except Exception as e:
            return {"tipo": "principal", "contenido": f"Error: {e}", "status": "error"}

    def _generate_comparative_content(self, section, fuentes_disponibles, variables_independientes):
        """Genera contenido comparativo y análisis crítico"""
        
        prompt = f"""
Como editor académico, desarrolla ANÁLISIS COMPARATIVO extenso para:

**SECCIÓN:** {section.title}
**VARIABLES:** {', '.join(variables_independientes)}

**INSTRUCCIONES PARA ANÁLISIS COMPARATIVO (800-1000 palabras):**
1. Comparación entre diferentes enfoques teóricos
2. Análisis de ventajas y limitaciones
3. Contrastes metodológicos
4. Debates contemporáneos
5. Síntesis integradora

**ELEMENTOS OBLIGATORIOS:**
- Tabla comparativa de enfoques/teorías
- Análisis de pros y contras
- Identificación de gaps de investigación
- Recomendaciones metodológicas

GENERA ANÁLISIS COMPARATIVO DETALLADO:
"""

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            return {
                "tipo": "comparativo",
                "contenido": response.content,
                "palabras": len(response.content.split()),
                "status": "completed"
            }
        except Exception as e:
            return {"tipo": "comparativo", "contenido": f"Error: {e}", "status": "error"}

    def _generate_variables_content(self, section, fuentes_disponibles, variables_independientes):
        """Genera contenido específico sobre variables independientes"""
        
        prompt = f"""
Como editor académico, desarrolla contenido específico sobre VARIABLES INDEPENDIENTES para:

**SECCIÓN:** {section.title}
**VARIABLES INDEPENDIENTES:** {', '.join(variables_independientes)}

**INSTRUCCIONES PARA CONTENIDO DE VARIABLES (600-800 palabras):**
1. Definición operacional de cada variable
2. Instrumentos de medición validados
3. Relaciones entre variables
4. Evidencia empírica disponible
5. Modelos teóricos que las incorporan

**ELEMENTOS OBLIGATORIOS:**
- Tabla de variables y definiciones operacionales
- Descripción de instrumentos de medición
- Análisis de relaciones causales
- Evidencia empírica reciente

GENERA CONTENIDO ESPECÍFICO SOBRE VARIABLES:
"""

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            return {
                "tipo": "variables",
                "contenido": response.content,
                "palabras": len(response.content.split()),
                "status": "completed"
            }
        except Exception as e:
            return {"tipo": "variables", "contenido": f"Error: {e}", "status": "error"}

    def get_agent_status(self):
        """
        Obtiene el estado actual del agente editor de fondo.
        
        Returns:
            Dict con información del estado del agente
        """
        return {
            "role": self.role.value,
            "model": OLLAMA_CONFIG["model"],
            "temperature": AGENT_CONFIG["editor_fondo"]["temperature"],
            "max_tokens": AGENT_CONFIG["editor_fondo"]["max_tokens"],
            "rag_initialized": self.rag_system is not None,
            "capabilities": [
                "generate_section_content",
                "enhance_paragraph",
                "create_transition_paragraph",
                "synthesize_concepts",
                "generate_content_piece",
                "generate_comprehensive_content"
            ],
            "variables_independientes": VARIABLES_INDEPENDIENTES
        }

    def __str__(self) -> str:
        return f"EditorFondoAgent(role={self.role.value}, model={OLLAMA_CONFIG['model']})"

    def __repr__(self) -> str:
        return self.__str__()
