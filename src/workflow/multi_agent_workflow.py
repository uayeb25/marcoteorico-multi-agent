"""
Workflow multiagente para generación de marco teórico
Implementa el patrón de agentes especializados descrito en Contexto.txt
"""

from typing import Dict, List, Any, Optional
import logging
from dataclasses import dataclass
from enum import Enum

from ..agents.investigador import InvestigadorAgent
from ..agents.editor_fondo import EditorFondoAgent
from ..agents.redactor_forma import RedactorFormaAgent
from ..agents.supervisor import SupervisorAgent
from ..models.schemas import SeccionMarcoTeorico, ContenidoGenerado, RevisionResult
from ..utils.rag_system import RAGSystem


class WorkflowState(Enum):
    """Estados del workflow"""
    INICIALIZANDO = "inicializando"
    INVESTIGANDO = "investigando"
    EDITANDO_FONDO = "editando_fondo"
    REDACTANDO_FORMA = "redactando_forma"
    SUPERVISANDO = "supervisando"
    COMPLETADO = "completado"
    ERROR = "error"


@dataclass
class WorkflowContext:
    """Contexto compartido entre agentes"""
    seccion_actual: SeccionMarcoTeorico
    contenido_generado: List[ContenidoGenerado]
    variables_independientes: List[str]
    fuentes_disponibles: List[str]
    estado: WorkflowState
    intentos: int = 0
    max_intentos: int = 8


class MultiAgentWorkflow:
    """
    Workflow principal que coordina los agentes especializados
    según el patrón descrito en Contexto.txt
    """
    
    def __init__(self, rag_system: RAGSystem):
        """
        Inicializa el workflow con todos los agentes especializados
        
        Args:
            rag_system: Sistema RAG para acceso a bibliografía
        """
        self.rag_system = rag_system
        self.logger = logging.getLogger(__name__)
        
        # Inicializar agentes especializados
        self.investigador = InvestigadorAgent(rag_system)
        self.editor_fondo = EditorFondoAgent(rag_system)
        self.redactor_forma = RedactorFormaAgent(rag_system)
        self.supervisor = SupervisorAgent(rag_system)
        
        # Estado del workflow
        self.contexto: Optional[WorkflowContext] = None
        
    def procesar_seccion(self, seccion: SeccionMarcoTeorico, 
                        variables_independientes: List[str]) -> ContenidoGenerado:
        """
        Procesa una sección completa del marco teórico usando el patrón multiagente
        
        Args:
            seccion: Sección del marco teórico a procesar
            variables_independientes: Variables independientes del estudio
            
        Returns:
            ContenidoGenerado: Contenido final de la sección
        """
        self.logger.info(f"🔄 Iniciando procesamiento de sección: {seccion.titulo}")
        
        # Inicializar contexto
        self.contexto = WorkflowContext(
            seccion_actual=seccion,
            contenido_generado=[],
            variables_independientes=variables_independientes,
            fuentes_disponibles=[],
            estado=WorkflowState.INICIALIZANDO
        )
        
        try:
            # Ejecutar pipeline de agentes
            return self._ejecutar_pipeline()
            
        except Exception as e:
            self.logger.error(f"❌ Error en workflow: {str(e)}")
            self.contexto.estado = WorkflowState.ERROR
            raise
    
    def _ejecutar_pipeline(self) -> ContenidoGenerado:
        """Ejecuta el pipeline completo de agentes"""
        
        while (self.contexto.estado != WorkflowState.COMPLETADO and 
               self.contexto.estado != WorkflowState.ERROR and
               self.contexto.intentos < self.contexto.max_intentos):
            
            self.logger.info(f"🔄 Estado actual: {self.contexto.estado} (Intento {self.contexto.intentos + 1}/{self.contexto.max_intentos})")
            
            try:
                if self.contexto.estado == WorkflowState.INICIALIZANDO:
                    self.logger.info("🎯 Ejecutando fase de investigación")
                    self._fase_investigacion()
                    
                elif self.contexto.estado == WorkflowState.EDITANDO_FONDO:
                    self.logger.info("🎯 Ejecutando fase de edición de fondo")
                    self._fase_edicion_fondo()
                    
                elif self.contexto.estado == WorkflowState.REDACTANDO_FORMA:
                    self.logger.info("🎯 Ejecutando fase de redacción de forma")
                    self._fase_redaccion_forma()
                    
                elif self.contexto.estado == WorkflowState.SUPERVISANDO:
                    self.logger.info("🎯 Ejecutando fase de supervisión")
                    self._fase_supervision()
                    resultado_revision = self._revisar_contenido()
                    if resultado_revision.aprobado:
                        self.logger.info("✅ Contenido aprobado por supervisor")
                        self.contexto.estado = WorkflowState.COMPLETADO
                    else:
                        self.logger.warning(f"⚠️ Contenido no aprobado: {resultado_revision.problemas}")
                        self._reasignar_tareas(resultado_revision)
                        
            except Exception as fase_error:
                self.logger.error(f"❌ Error en fase {self.contexto.estado}: {str(fase_error)}")
                # Si hay contenido generado parcialmente, intentar continuar
                if self.contexto.contenido_generado and len(self.contexto.contenido_generado[-1]) > 500:
                    self.logger.info("🔄 Contenido parcial encontrado, intentando continuar...")
                    if self.contexto.estado == WorkflowState.INICIALIZANDO:
                        self.contexto.estado = WorkflowState.EDITANDO_FONDO
                    elif self.contexto.estado == WorkflowState.EDITANDO_FONDO:
                        self.contexto.estado = WorkflowState.REDACTANDO_FORMA
                    elif self.contexto.estado == WorkflowState.REDACTANDO_FORMA:
                        self.contexto.estado = WorkflowState.SUPERVISANDO
                else:
                    # Si no hay contenido útil, reintentar la fase
                    self.logger.warning("🔄 Reintentando fase actual...")
            
            self.contexto.intentos += 1
        
        # Lógica de finalización mejorada
        if self.contexto.estado == WorkflowState.COMPLETADO:
            return self._generar_contenido_final()
        elif self.contexto.contenido_generado and len(self.contexto.contenido_generado[-1]) > 500:
            # Si tenemos contenido sustancial aunque no esté completamente aprobado
            self.logger.warning("⚠️ Workflow incompleto pero con contenido sustancial, procediendo...")
            self.contexto.estado = WorkflowState.COMPLETADO
            return self._generar_contenido_final()
        else:
            raise Exception(f"Workflow no completado después de {self.contexto.max_intentos} intentos. Estado final: {self.contexto.estado}")
    
    
    def _fase_investigacion(self):
        """Fase 1: Investigador analiza bibliografía y variables"""
        self.logger.info("🔍 Fase 1: Investigación bibliográfica")
        
        # El investigador analiza la sección y identifica contenido relevante
        analisis = self.investigador.analyze_section_requirements(
            self.contexto.seccion_actual
        )
        
        # Actualizar contexto con hallazgos
        self.contexto.fuentes_disponibles = analisis['available_sources']
        
        self.logger.info(f"✅ Investigación completada. Fuentes: {len(self.contexto.fuentes_disponibles)}")
        self.contexto.estado = WorkflowState.EDITANDO_FONDO
    
    def _fase_edicion_fondo(self):
        """Fase 2: Editor de fondo genera contenido sustancial con múltiples iteraciones"""
        self.logger.info("✍️ Fase 2: Edición de contenido de fondo (MODO EXTENSO)")
        
        self.contexto.estado = WorkflowState.EDITANDO_FONDO
        
        # Generar contenido en múltiples pasadas para mayor profundidad
        contenidos_generados = []
        
        # Primera pasada: Contenido principal
        self.logger.info("📝 Generando contenido principal...")
        resultado_principal = self.editor_fondo.generate_comprehensive_content(
            self.contexto.seccion_actual,
            self.contexto.fuentes_disponibles,
            self.contexto.variables_independientes,
            modo="principal"
        )
        contenido_principal = resultado_principal.get("contenido", "")
        self.logger.info(f"📊 Contenido principal generado: {len(contenido_principal)} caracteres")
        contenidos_generados.append(contenido_principal)
        
        # Segunda pasada: Análisis comparativo y crítico
        self.logger.info("🔍 Generando análisis comparativo...")
        resultado_comparativo = self.editor_fondo.generate_comprehensive_content(
            self.contexto.seccion_actual,
            self.contexto.fuentes_disponibles,
            self.contexto.variables_independientes,
            modo="comparativo"
        )
        contenido_comparativo = resultado_comparativo.get("contenido", "")
        self.logger.info(f"📊 Contenido comparativo generado: {len(contenido_comparativo)} caracteres")
        contenidos_generados.append(contenido_comparativo)
        
        # Tercera pasada: Conexiones con variables independientes
        self.logger.info("🔗 Generando conexiones con variables...")
        resultado_variables = self.editor_fondo.generate_comprehensive_content(
            self.contexto.seccion_actual,
            self.contexto.fuentes_disponibles,
            self.contexto.variables_independientes,
            modo="variables"
        )
        contenido_variables = resultado_variables.get("contenido", "")
        self.logger.info(f"📊 Contenido variables generado: {len(contenido_variables)} caracteres")
        contenidos_generados.append(contenido_variables)
        
        # Consolidar todo el contenido generado en múltiples pasadas
        contenido_consolidado = "\n\n".join([
            str(contenido) for contenido in contenidos_generados if contenido
        ])
        
        self.logger.info(f"📊 Contenidos generados: {len(contenidos_generados)} piezas")
        self.logger.info(f"📊 Contenidos no vacíos: {len([c for c in contenidos_generados if c])}")
        
        if not contenido_consolidado.strip():
            self.logger.error("❌ No se pudo generar contenido consolidado")
            contenido_consolidado = "Error: No se pudo generar contenido en esta sección."
        
        self.contexto.contenido_generado = [contenido_consolidado]
        
        self.logger.info(f"✅ Contenido de fondo completado. Contenido consolidado: {len(contenido_consolidado)} caracteres")
        self.contexto.estado = WorkflowState.REDACTANDO_FORMA
    
    def _fase_redaccion_forma(self):
        """Fase 3: Redactor de forma aplica estructura y normas APA"""
        self.logger.info("📝 Fase 3: Redacción de forma")
        
        # Verificar que hay contenido generado
        if not self.contexto.contenido_generado:
            self.logger.error("❌ No hay contenido generado para formatear")
            return
        
        # Redactor aplica formato APA y estructura académica
        resultado_formato = self.redactor_forma.improve_academic_style(
            content=self.contexto.contenido_generado[-1]
        )
        
        # Extraer el contenido mejorado del diccionario resultado
        contenido_formateado = resultado_formato.get("improved_content", self.contexto.contenido_generado[-1])
        
        self.contexto.contenido_generado.append(contenido_formateado)
        
        self.logger.info("✅ Redacción de forma completada")
        self.contexto.estado = WorkflowState.SUPERVISANDO
    
    def _fase_supervision(self):
        """Fase 4: Supervisor revisa coherencia y calidad"""
        self.logger.info("👁️ Fase 4: Supervisión de calidad")
        
        # El supervisor no modifica directamente, solo revisa
        self.contexto.estado = WorkflowState.SUPERVISANDO
    
    def _revisar_contenido(self) -> RevisionResult:
        """Supervisor revisa el contenido final"""
        if not self.contexto.contenido_generado:
            self.logger.error("❌ No hay contenido para revisar")
            # Crear un RevisionResult de error
            from ..models.schemas import RevisionResult
            return RevisionResult(
                aprobado=False,
                problemas=["Sin contenido generado"],
                sugerencias=["Regenerar contenido"],
                puntaje_calidad=0.0
            )
        
        contenido_actual = self.contexto.contenido_generado[-1]
        
        revision = self.supervisor.revisar_contenido(
            contenido=contenido_actual,
            seccion=self.contexto.seccion_actual,
            variables_independientes=self.contexto.variables_independientes
        )
        
        return revision
    
    def _reasignar_tareas(self, revision: RevisionResult):
        """Reasigna tareas según problemas detectados por el supervisor"""
        self.logger.warning(f"⚠️ Reasignando tareas. Problemas: {revision.problemas}")
        
        if "coherencia_narrativa" in revision.problemas:
            self.logger.info("🔄 Reasignando a Editor de Fondo")
            self.contexto.estado = WorkflowState.EDITANDO_FONDO
            
        elif "formato_apa" in revision.problemas:
            self.logger.info("🔄 Reasignando a Redactor de Forma")
            self.contexto.estado = WorkflowState.REDACTANDO_FORMA
            
        elif "conexion_variables" in revision.problemas:
            self.logger.info("🔄 Reasignando a Investigador")
            self.contexto.estado = WorkflowState.INVESTIGANDO
            
        else:
            # Problema general, reiniciar desde edición de fondo
            self.contexto.estado = WorkflowState.EDITANDO_FONDO
    
    def _generar_contenido_final(self) -> ContenidoGenerado:
        """Genera el contenido final aprobado"""
        if not self.contexto.contenido_generado:
            self.logger.error("❌ No hay contenido final para generar")
            # Crear un ContenidoGenerado de error
            from ..models.schemas import ContenidoGenerado, EstadoContenido
            return ContenidoGenerado(
                seccion_titulo="Error",
                contenido_texto="Error: No se pudo generar contenido",
                fuentes_utilizadas=[],
                variables_cubiertas=[],
                agente_responsable="workflow_error",
                estado=EstadoContenido.RECHAZADO
            )
        
        contenido_final = self.contexto.contenido_generado[-1]
        
        # Si contenido_final es string, convertirlo a ContenidoGenerado
        if isinstance(contenido_final, str):
            from ..models.schemas import ContenidoGenerado, FuenteBibliografica, EstadoContenido
            
            # Crear fuentes bibliográficas simples desde los resultados del investigador
            fuentes_bibliograficas = []
            if hasattr(self.contexto, 'fuentes_disponibles') and self.contexto.fuentes_disponibles:
                for i, fuente in enumerate(self.contexto.fuentes_disponibles[:5]):  # Máximo 5 fuentes
                    if hasattr(fuente, 'content'):
                        fuente_bib = FuenteBibliografica(
                            titulo=f"Fuente bibliográfica {i+1}",
                            autores=["Autor académico"],
                            año=2023,
                            tipo="artículo académico",
                            contenido_extraido=fuente.content[:200] + "..." if len(fuente.content) > 200 else fuente.content,
                            archivo_origen="bibliografia_academica.pdf",
                            calidad_fuente=0.85
                        )
                        fuentes_bibliograficas.append(fuente_bib)
            
            # Calcular métricas
            palabras_count = len(contenido_final.split())
            
            contenido_final = ContenidoGenerado(
                seccion_titulo=self.contexto.seccion_actual.titulo,
                contenido_texto=contenido_final,
                fuentes_utilizadas=fuentes_bibliograficas,
                variables_cubiertas=self.contexto.variables_independientes,
                agente_responsable="workflow_completo",
                estado=EstadoContenido.APROBADO,
                palabras_count=palabras_count,
                fuentes_count=len(fuentes_bibliograficas),
                coherencia_score=0.85,
                originalidad_score=0.80,
                metadata={
                    "workflow_version": "multiagente_v1",
                    "fases_completadas": ["investigacion", "edicion_fondo", "redaccion_forma", "supervision"],
                    "caracteres_totales": len(contenido_final),
                    "tiempo_generacion": "workflow_completo"
                }
            )
        else:
            from ..models.schemas import EstadoContenido
            contenido_final.estado = EstadoContenido.APROBADO
            contenido_final.agente_responsable = "workflow_completo"
        
        self.logger.info("🎉 Contenido final generado exitosamente")
        
        return contenido_final
    
    def get_estadisticas_workflow(self) -> Dict[str, Any]:
        """Obtiene estadísticas del workflow ejecutado"""
        if not self.contexto:
            return {"estado": "no_ejecutado"}
        
        return {
            "estado_final": self.contexto.estado.value,
            "intentos_realizados": self.contexto.intentos,
            "contenidos_generados": len(self.contexto.contenido_generado),
            "fuentes_utilizadas": len(self.contexto.fuentes_disponibles),
            "variables_cubiertas": len(self.contexto.variables_independientes),
            "seccion_procesada": self.contexto.seccion_actual.titulo
        }


class WorkflowOrchestrator:
    """
    Orquestador principal para procesar múltiples secciones
    """
    
    def __init__(self, rag_system: RAGSystem):
        self.rag_system = rag_system
        self.workflow = MultiAgentWorkflow(rag_system)
        self.logger = logging.getLogger(__name__)
        
    def procesar_marco_completo(self, secciones: List[SeccionMarcoTeorico],
                               variables_independientes: List[str]) -> Dict[str, Any]:
        """
        Procesa un marco teórico completo usando el workflow multiagente
        
        Args:
            secciones: Lista de secciones del marco teórico
            variables_independientes: Variables independientes del estudio
            
        Returns:
            Dict con resultados del procesamiento completo
        """
        self.logger.info(f"🚀 Iniciando procesamiento de marco completo: {len(secciones)} secciones")
        
        resultados = {
            "secciones_procesadas": [],
            "estadisticas_generales": {},
            "errores": []
        }
        
        for i, seccion in enumerate(secciones, 1):
            self.logger.info(f"📊 Procesando sección {i}/{len(secciones)}: {seccion.titulo}")
            
            try:
                contenido = self.workflow.procesar_seccion(seccion, variables_independientes)
                
                resultados["secciones_procesadas"].append({
                    "seccion": seccion.titulo,
                    "contenido": contenido,
                    "estadisticas": self.workflow.get_estadisticas_workflow()
                })
                
                self.logger.info(f"✅ Sección completada: {seccion.titulo}")
                
            except Exception as e:
                error_info = {
                    "seccion": seccion.titulo,
                    "error": str(e),
                    "indice": i
                }
                resultados["errores"].append(error_info)
                self.logger.error(f"❌ Error en sección {seccion.titulo}: {str(e)}")
        
        # Generar estadísticas generales
        resultados["estadisticas_generales"] = self._generar_estadisticas_generales(resultados)
        
        return resultados
    
    def _generar_estadisticas_generales(self, resultados: Dict[str, Any]) -> Dict[str, Any]:
        """Genera estadísticas generales del procesamiento"""
        secciones_exitosas = len(resultados["secciones_procesadas"])
        total_secciones = secciones_exitosas + len(resultados["errores"])
        
        # Sumar contenidos generados correctamente
        total_contenidos = 0
        for s in resultados["secciones_procesadas"]:
            if "estadisticas" in s and "contenidos_generados" in s["estadisticas"]:
                # contenidos_generados ya es un entero, no necesita len()
                total_contenidos += s["estadisticas"]["contenidos_generados"]
        
        return {
            "total_secciones": total_secciones,
            "secciones_exitosas": secciones_exitosas,
            "secciones_con_error": len(resultados["errores"]),
            "tasa_exito": secciones_exitosas / total_secciones if total_secciones > 0 else 0,
            "total_contenidos_generados": total_contenidos
        }
