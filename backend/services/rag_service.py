"""
RAG Service - Retrieval Augmented Generation
Processa o manual técnico e responde perguntas baseadas no conteúdo
"""
import os
import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict


class RAGService:
    def __init__(self):
        # Inicializar ChromaDB
        self.client = chromadb.PersistentClient(path="./data/chroma_db")
        
        # Função de embedding (usa modelo local sentence-transformers)
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
        
        # Criar ou carregar coleção
        try:
            self.collection = self.client.get_collection(
                name="manual_tecnico",
                embedding_function=self.embedding_function
            )
            print("[RAG] Coleção carregada com sucesso")
        except:
            self.collection = self.client.create_collection(
                name="manual_tecnico",
                embedding_function=self.embedding_function
            )
            print("[RAG] Nova coleção criada")
            self._load_manual()
    
    def _load_manual(self):
        """Carrega o manual técnico e indexa no ChromaDB"""
        manual_path = "./data/manual_tecnico.txt"
        
        if not os.path.exists(manual_path):
            print("[RAG] Manual não encontrado!")
            return
        
        with open(manual_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Dividir em chunks (parágrafos)
        chunks = []
        current_chunk = ""
        
        for line in content.split('\n'):
            if line.startswith('##'):  # Novo tópico
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = line + '\n'
            else:
                current_chunk += line + '\n'
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        # Indexar chunks
        ids = [f"chunk_{i}" for i in range(len(chunks))]
        
        self.collection.add(
            documents=chunks,
            ids=ids
        )
        
        print(f"[RAG] {len(chunks)} chunks indexados!")
    
    def search(self, query: str, n_results: int = 3) -> List[str]:
        """
        Busca contexto relevante no manual
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            documents = results['documents'][0] if results['documents'] else []
            print(f"[RAG] Encontrados {len(documents)} resultados para: '{query}'")
            
            return documents
        except Exception as e:
            print(f"[RAG] Erro na busca: {str(e)}")
            return []
    
    def get_context_for_question(self, question: str) -> str:
        """
        Retorna contexto formatado para usar com o Gemini
        """
        documents = self.search(question, n_results=3)
        
        if not documents:
            return ""
        
        context = "INFORMAÇÕES DO MANUAL TÉCNICO:\n\n"
        for i, doc in enumerate(documents, 1):
            context += f"[Trecho {i}]\n{doc}\n\n"
        
        return context
    
    def is_technical_question(self, message: str) -> bool:
        """
        Verifica se a pergunta é técnica (deve usar RAG)
        """
        technical_keywords = [
            'especificação', 'diferença', 'melhor', 'comparar', 'vale a pena',
            'ram', 'processador', 'ssd', 'gpu', 'bateria', 'tela', 'câmera',
            'quanto custa', 'qual', 'como funciona', 'o que é', 'explicar',
            'recomenda', 'preciso de', 'qual escolher', 'garantia', 'troca',
            'devolução', 'entrega', 'prazo', 'pagamento'
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in technical_keywords)
