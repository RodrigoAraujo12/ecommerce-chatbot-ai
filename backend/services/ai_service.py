"""
AI Service for handling Google Gemini API calls
"""
import os
import json
from typing import List, Dict, Optional, Any
from google import genai
from google.genai import types
from .rag_service import RAGService


class AIService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None
        
        # Inicializar RAG
        try:
            self.rag = RAGService()
            print("[AI Service] RAG inicializado com sucesso")
        except Exception as e:
            print(f"[AI Service] Erro ao inicializar RAG: {str(e)}")
            self.rag = None
    
    async def generate_response_with_functions(
        self, 
        messages: List[Dict[str, str]],
        available_functions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Gera resposta da IA com detecção automática de busca de produtos
        """
        if not self.client:
            return {
                "type": "text",
                "content": "Erro: API key do Google Gemini não configurada."
            }
        
        try:
            last_message = messages[-1]["content"] if messages else ""
            
            # 1. Verificar se é pergunta técnica (RAG)
            if self.rag and self.rag.is_technical_question(last_message):
                print("[AI Service] Pergunta técnica detectada - usando RAG")
                context = self.rag.get_context_for_question(last_message)
                
                if context:
                    # Responder usando contexto do manual
                    prompt = f"""{context}

PERGUNTA DO USUÁRIO: {last_message}

Responda baseado nas informações do manual técnico acima. Seja claro, objetivo e útil."""
                    
                    response = self.client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            temperature=0.2
                        )
                    )
                    
                    return {
                        "type": "text",
                        "content": response.text
                    }
            
            # 2. Verificar se quer buscar produtos
            should_search, params = self._analyze_intent_and_extract(last_message)
            
            if should_search:
                # Garantir query mínima
                if 'query' not in params:
                    params['query'] = last_message
                print(f"[AI Service] Chamando busca com: {params}")
                return {
                    "type": "function_call",
                    "function": "search_products",
                    "arguments": params
                }
            
            # 3. Resposta normal da IA
            conversation_text = self.get_system_prompt() + "\n\n"
            for msg in messages:
                role = "Usuário" if msg["role"] == "user" else "Assistente"
                conversation_text += f"{role}: {msg['content']}\n"
            
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=conversation_text,
                config=types.GenerateContentConfig(
                    temperature=0.2
                )
            )
            
            return {
                "type": "text",
                "content": response.text
            }
            
        except Exception as e:
            print(f"[AI Service] Erro: {str(e)}")
            return {
                "type": "text",
                "content": f"Desculpe, ocorreu um erro ao processar sua mensagem."
            }
    
    def _analyze_intent_and_extract(self, message: str) -> tuple[bool, Dict]:
        """
        Análise única: detecta intenção E extrai parâmetros em 1 só chamada!
        Retorna: (deve_buscar, parametros)
        """
        if not self.client:
            return False, {}
        
        try:
            # Prompt combinado - muito mais eficiente!
            analysis_prompt = f"""Analise esta mensagem e responda no formato exato:

Mensagem: "{message}"

BUSCAR: [SIM ou NAO] - O usuário quer buscar produtos?
PRODUTO: [texto ou "nada"] - Qual produto buscar?
PRECO: [número ou "nao"] - Tem limite de preço?

Exemplos:

Mensagem: "procure celular samsung até 3000 reais"
BUSCAR: SIM
PRODUTO: celular samsung
PRECO: 3000

Mensagem: "queria saber o preço do Samsung Galaxy S8"
BUSCAR: SIM
PRODUTO: samsung galaxy s8
PRECO: nao

Mensagem: "olá, como você funciona?"
BUSCAR: NAO
PRODUTO: nada
PRECO: nao"""

            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=analysis_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2
                )
            )
            
            result_text = response.text
            print(f"[AI Service] Análise completa:\n{result_text}")
            
            # Parse
            should_search = "BUSCAR: SIM" in result_text.upper()
            params = {}
            
            if should_search:
                # Extrair produto
                if "PRODUTO:" in result_text:
                    produto_line = [line for line in result_text.split('\n') if 'PRODUTO:' in line][0]
                    produto = produto_line.split('PRODUTO:')[1].strip()
                    if produto.lower() != "nada":
                        params['query'] = produto
                
                # Extrair preço
                if "PRECO:" in result_text:
                    preco_line = [line for line in result_text.split('\n') if 'PRECO:' in line][0]
                    preco_str = preco_line.split('PRECO:')[1].strip().lower()
                    if preco_str not in ["nao", "não", "nada"]:
                        try:
                            params['max_price'] = float(preco_str.replace(',', '.'))
                        except:
                            pass
            
            return should_search, params
            
        except Exception as e:
            print(f"[AI Service] Erro na análise: {str(e)}")
            # Fallback para keywords
            keywords = ['procur', 'busca', 'encontr', 'quero', 'preciso', 'tem ', 'preço', 'preco', 'quanto custa']
            should_search = any(kw in message.lower() for kw in keywords)
            return should_search, {'query': message} if should_search else {}
    
    def _extract_search_params(self, message: str) -> Dict:
        """
        Usa o Gemini para extrair parâmetros de busca de forma inteligente
        """
        try:
            # Prompt para extrair informações estruturadas
            extraction_prompt = f"""Analise esta mensagem e extraia as informações de busca.

Mensagem: "{message}"

Extraia:
1. PRODUTO: Qual produto o usuário quer buscar? (exemplo: "celular", "notebook", "samsung galaxy s8")
2. PRECO_MAXIMO: Tem limite de preço? Extraia apenas o número. Se não tiver, retorne "nao"

Responda no formato exato:
PRODUTO: [texto aqui]
PRECO: [número ou "nao"]

Exemplos:
Mensagem: "procure celular samsung até 3000 reais"
PRODUTO: celular samsung
PRECO: 3000

Mensagem: "queria saber o preço do Samsung Galaxy S8"
PRODUTO: samsung galaxy s8
PRECO: nao

Mensagem: "tem notebook Dell com SSD?"
PRODUTO: notebook dell ssd
PRECO: nao"""

            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=extraction_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2
                )
            )
            
            result_text = response.text
            print(f"[AI Service] Extração Gemini:\n{result_text}")
            
            # Parse da resposta
            params = {}
            
            # Extrair produto
            if "PRODUTO:" in result_text:
                produto_line = [line for line in result_text.split('\n') if 'PRODUTO:' in line][0]
                produto = produto_line.split('PRODUTO:')[1].strip()
                params['query'] = produto
            else:
                params['query'] = message
            
            # Extrair preço
            if "PRECO:" in result_text:
                preco_line = [line for line in result_text.split('\n') if 'PRECO:' in line][0]
                preco_str = preco_line.split('PRECO:')[1].strip().lower()
                if preco_str != "nao" and preco_str != "não":
                    try:
                        params['max_price'] = float(preco_str.replace(',', '.'))
                    except:
                        pass
            
            print(f"[AI Service] Parâmetros extraídos: {params}")
            return params
            
        except Exception as e:
            print(f"[AI Service] Erro na extração Gemini: {str(e)}")
            # Fallback para método regex
            return self._extract_search_params_fallback(message)
    
    def _extract_search_params_fallback(self, message: str) -> Dict:
        """
        Fallback: extração por regex quando Gemini falha
        """
        params = {}
        message_lower = message.lower()
        
        # Extrair preço máximo
        import re
        price_patterns = [
            r'até\s*r?\$?\s*(\d+(?:\.\d{3})*(?:,\d{2})?)',
            r'máximo\s*(?:de\s*)?r?\$?\s*(\d+(?:\.\d{3})*(?:,\d{2})?)',
            r'r?\$?\s*(\d+(?:\.\d{3})*(?:,\d{2})?)\s*reais',
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, message_lower)
            if match:
                price_str = match.group(1).replace('.', '').replace(',', '.')
                try:
                    params["max_price"] = float(price_str)
                    break
                except:
                    pass
        
        # Extrair query (remover palavras de ação e preço)
        query = message
        # Remover menções de preço
        query = re.sub(r'até\s*r?\$?\s*\d+[\d.,]*', '', query, flags=re.IGNORECASE)
        query = re.sub(r'máximo\s*(?:de\s*)?r?\$?\s*\d+[\d.,]*', '', query, flags=re.IGNORECASE)
        query = re.sub(r'r?\$?\s*\d+[\d.,]*\s*reais', '', query, flags=re.IGNORECASE)
        
        params["query"] = query.strip()
        
        print(f"[AI Service] Parâmetros extraídos: {params}")
        
        return params
    
    def _format_functions_for_prompt(self) -> str:
        """
        Formata funções disponíveis para incluir no prompt
        """
        return """
Você tem acesso às seguintes ferramentas:
- search_products: Busca produtos no Mercado Livre

Quando o usuário pedir para procurar produtos, você deve usar essa ferramenta.
        """
    
    def get_system_prompt(self) -> str:
        """
        Get system prompt for the AI assistant
        """
        return """Você é um assistente virtual de atendimento ao cliente para e-commerce.
        Você pode ajudar clientes com:
        - Status e rastreamento de pedidos
        - Informações sobre produtos e disponibilidade
        - Políticas de troca e devolução
        - Perguntas gerais sobre a loja
        
        Seja profissional, amigável e objetivo em suas respostas. Responda sempre em português."""
    
    async def generate_response(self, messages: List[Dict[str, str]]) -> str:
        """
        Método legado para compatibilidade (sem function calling)
        """
        result = await self.generate_response_with_functions(messages, {})
        if result["type"] == "text":
            return result["content"]
        return "Processando sua solicitação..."