"""
Sistema RAG (Retrieval-Augmented Generation) para el procesamiento de bibliografía
"""
import os
import uuid
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_ollama import OllamaLLM
from langchain.schema import Document

from ..models.schemas import BibliographySource, RAGQuery, RAGResult
from config import CHROMA_CONFIG, WORKFLOW_CONFIG, OLLAMA_CONFIG

class RAGSystem:
    """Sistema RAG para procesamiento y consulta de bibliografía"""
    
    def __init__(self, model_name: str = "llama3.1:8b"):
        """
        Inicializa el sistema RAG con el modelo especificado.
        
        Args:
            model_name: Nombre del modelo Ollama a usar (por defecto llama3.1:8b para mejor rendimiento académico)
        """
        print(f"🤖 Inicializando RAG con modelo: {model_name}")
        
        # Configurar embeddings con modelo especificado
        self.embeddings = OllamaEmbeddings(
            model="nomic-embed-text",
            base_url="http://localhost:11434"
        )
        
        # Configurar LLM con modelo especificado
        self.llm = OllamaLLM(
            model=model_name,
            base_url="http://localhost:11434",
            temperature=0.3,  # Reducir temperatura para mayor precisión académica
            num_ctx=4096      # Aumentar contexto para textos académicos largos
        )
        
        # Configurar ChromaDB
        self.chroma_client = chromadb.PersistentClient(
            path=CHROMA_CONFIG["persist_directory"]
        )
        
        try:
            self.collection = self.chroma_client.get_collection(
                name=CHROMA_CONFIG["collection_name"]
            )
        except:
            self.collection = self.chroma_client.create_collection(
                name=CHROMA_CONFIG["collection_name"],
                metadata={"description": "Colección de bibliografía para marco teórico"}
            )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=WORKFLOW_CONFIG["chunk_size"],
            chunk_overlap=WORKFLOW_CONFIG["overlap"],
            separators=["\\n\\n", "\\n", ".", "!", "?", ",", " ", ""]
        )
    
    def process_pdf(self, file_path: str) -> BibliographySource:
        """
        Procesa un archivo PDF y lo almacena en la base de datos vectorial
        
        Args:
            file_path: Ruta al archivo PDF
            
        Returns:
            BibliographySource: Fuente procesada
        """
        # Cargar PDF
        loader = PyPDFLoader(file_path)
        pages = loader.load()
        
        # Extraer metadatos básicos
        title = os.path.basename(file_path).replace(".pdf", "")
        
        # Combinar todo el texto
        full_text = "\\n".join([page.page_content for page in pages])
        
        # Dividir en chunks
        chunks = self.text_splitter.split_text(full_text)
        
        # Generar embeddings y almacenar en ChromaDB
        embedding_ids = []
        metadatas = []
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"{title}_{i}_{uuid.uuid4().hex[:8]}"
            embedding_ids.append(chunk_id)
            
            metadatas.append({
                "source": title,
                "file_path": file_path,
                "chunk_index": i,
                "chunk_id": chunk_id
            })
        
        # Generar embeddings
        embeddings = [self.embeddings.embed_query(chunk) for chunk in chunks]
        
        # Almacenar en ChromaDB
        self.collection.add(
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas,
            ids=embedding_ids
        )
        
        # Crear BibliographySource
        source = BibliographySource(
            id=str(uuid.uuid4()),
            title=title,
            file_path=file_path,
            content_chunks=chunks,
            embedding_ids=embedding_ids
        )
        
        return source
    
    def process_bibliography_folder(self, folder_path: str) -> List[BibliographySource]:
        """
        Procesa todos los PDFs en una carpeta
        
        Args:
            folder_path: Ruta a la carpeta con PDFs
            
        Returns:
            List[BibliographySource]: Lista de fuentes procesadas
        """
        sources = []
        
        for filename in os.listdir(folder_path):
            if filename.lower().endswith('.pdf'):
                file_path = os.path.join(folder_path, filename)
                try:
                    source = self.process_pdf(file_path)
                    sources.append(source)
                    print(f"Procesado: {filename}")
                except Exception as e:
                    print(f"Error procesando {filename}: {e}")
        
        return sources
    
    def query(self, rag_query: RAGQuery) -> RAGResult:
        """
        Realiza una consulta al sistema RAG
        
        Args:
            rag_query: Consulta RAG con parámetros
            
        Returns:
            RAGResult: Resultados de la consulta
        """
        # Generar embedding de la consulta
        query_embedding = self.embeddings.embed_query(rag_query.query)
        
        # Buscar en ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=rag_query.max_results,
            include=["documents", "metadatas", "distances"]
        )
        
        # Procesar resultados
        chunks = results["documents"][0] if results["documents"] else []
        metadatas = results["metadatas"][0] if results["metadatas"] else []
        distances = results["distances"][0] if results["distances"] else []
        
        # Convertir distancias a scores (similitud)
        scores = [1 - dist for dist in distances]
        
        # Extraer fuentes
        sources = [meta.get("source", "Unknown") for meta in metadatas]
        
        return RAGResult(
            chunks=chunks,
            sources=sources,
            scores=scores,
            metadata={
                "query": rag_query.query,
                "num_results": len(chunks),
                "max_score": max(scores) if scores else 0
            }
        )
    
    def get_relevant_content(self, section_title: str, variables: List[str], max_results: int = 5) -> RAGResult:
        """
        Obtiene contenido relevante para una sección específica
        
        Args:
            section_title: Título de la sección
            variables: Variables independientes relacionadas
            max_results: Número máximo de resultados
            
        Returns:
            RAGResult: Contenido relevante encontrado
        """
        # Construir query combinando sección y variables
        query_parts = [section_title]
        query_parts.extend(variables)
        combined_query = " ".join(query_parts)
        
        rag_query = RAGQuery(
            query=combined_query,
            section_context=section_title,
            variables_filter=variables,
            max_results=max_results
        )
        
        return self.query(rag_query)
    
    def clear_collection(self):
        """Limpia la colección de ChromaDB"""
        try:
            self.chroma_client.delete_collection(CHROMA_CONFIG["collection_name"])
            self.collection = self.chroma_client.create_collection(
                name=CHROMA_CONFIG["collection_name"],
                metadata={"description": "Colección de bibliografía para marco teórico"}
            )
        except Exception as e:
            print(f"Error limpiando colección: {e}")
    
    def clear_context_chunks(self):
        """Limpia solo los chunks de contexto previo, manteniendo los PDFs originales"""
        try:
            # Obtener todos los documentos con metadata
            result = self.collection.get(include=['metadatas'])
            
            # Encontrar IDs de chunks de contexto previo
            context_ids = []
            for i, metadata in enumerate(result['metadatas']):
                if metadata.get('source') == 'contexto_previo' or metadata.get('content_type') == 'contexto_previo':
                    context_ids.append(result['ids'][i])
            
            # Eliminar chunks de contexto previo
            if context_ids:
                self.collection.delete(ids=context_ids)
                print(f"🧹 Eliminados {len(context_ids)} chunks de contexto previo")
            else:
                print("ℹ️ No se encontraron chunks de contexto previo para limpiar")
                
        except Exception as e:
            print(f"Error limpiando chunks de contexto: {e}")
    
    def add_context_content(self, context_content: str, source_name: str = "contexto_previo"):
        """
        Agrega contenido de contexto previo a la base vectorial
        Limpia chunks de contexto anteriores antes de agregar nuevos
        
        Args:
            context_content: Contenido de contexto a agregar
            source_name: Nombre de la fuente del contexto
        """
        # Limpiar chunks de contexto previo antes de agregar nuevos
        self.clear_context_chunks()
        
        # Dividir el contenido en chunks
        chunks = self.text_splitter.split_text(context_content)
        
        if not chunks:
            return
        
        # Generar embeddings y metadatos
        embedding_ids = []
        metadatas = []
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"{source_name}_{i}_{uuid.uuid4().hex[:8]}"
            embedding_ids.append(chunk_id)
            
            metadatas.append({
                "source": source_name,
                "file_path": "contexto_generado",
                "chunk_index": i,
                "chunk_id": chunk_id,
                "content_type": "contexto_previo"
            })
        
        # Generar embeddings
        embeddings = [self.embeddings.embed_query(chunk) for chunk in chunks]
        
        # Almacenar en ChromaDB
        self.collection.add(
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas,
            ids=embedding_ids
        )
        
        print(f"✅ Agregados {len(chunks)} chunks de contexto a la BD vectorial")

    def get_collection_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de la colección"""
        try:
            count = self.collection.count()
            return {
                "total_documents": count,
                "collection_name": CHROMA_CONFIG["collection_name"],
                "persist_directory": CHROMA_CONFIG["persist_directory"]
            }
        except Exception as e:
            return {"error": str(e)}
