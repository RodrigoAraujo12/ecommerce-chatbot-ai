"""
Public E-commerce APIs Integration
APIs: DummyJSON (https://dummyjson.com) + FakeStore API (https://fakestoreapi.com)
Gratuitas, sem autenticação, sem bloqueios!
"""
import httpx
from typing import List, Dict, Optional
import random


class ProductService:
    def __init__(self):
        self.apis = {
            "dummyjson": "https://dummyjson.com",
            "fakestoreapi": "https://fakestoreapi.com"
        }
    
    async def search_products(
        self, 
        query: str, 
        max_price: Optional[float] = None,
        limit: int = 5
    ) -> List[Dict]:
        """
        Busca produtos em APIs públicas (DummyJSON ou Fake Store API)
        """
        cleaned_query = self._clean_query(query)
        print(f"[Public API] Buscando: '{cleaned_query}'")
        
        try:
            # Buscar mais produtos para compensar filtro de preço
            search_limit = limit * 4 if max_price else limit * 2
            
            # Tentar DummyJSON primeiro (mais completa)
            products = await self._search_dummyjson(cleaned_query, search_limit)
            
            # Se não encontrou nada com termo específico, tentar termo genérico
            if not products and ' ' in cleaned_query:
                # Pegar apenas a primeira palavra (categoria genérica)
                generic_term = cleaned_query.split()[0]
                print(f"[Public API] Tentando busca genérica: '{generic_term}'")
                products = await self._search_dummyjson(generic_term, search_limit)
            
            if not products:
                # Fallback para Fake Store API
                print("[Public API] Tentando FakeStore API...")
                products = await self._search_fakestoreapi(cleaned_query, search_limit)
                
                # Se ainda não achou, tentar termo genérico na FakeStore
                if not products and ' ' in cleaned_query:
                    generic_term = cleaned_query.split()[0]
                    print(f"[Public API] FakeStore com termo genérico: '{generic_term}'")
                    products = await self._search_fakestoreapi(generic_term, search_limit)
            
            if products:
                print(f"[Public API] Total encontrado: {len(products)} produtos")
                
                # Filtrar por preço
                if max_price:
                    before = len(products)
                    products = [p for p in products if p.get("price", 0) <= max_price]
                    print(f"[Public API] Após filtrar por R$ {max_price}: {len(products)} produtos")
                
                # Limitar quantidade final
                products = products[:limit]
                print(f"[Public API] ✅ Retornando {len(products)} produtos!")
                return products
            
            print("[Public API] ⚠️ Nenhum produto encontrado")
            return []
            
        except Exception as e:
            print(f"[Public API] ❌ Erro: {str(e)}")
            return []
    
    async def _search_dummyjson(self, query: str, limit: int) -> Optional[List[Dict]]:
        """
        DummyJSON API - https://dummyjson.com/products/search?q=phone
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                url = f"{self.apis['dummyjson']}/products/search"
                params = {"q": query, "limit": min(limit, 30)}
                
                print(f"[DummyJSON] GET {url}?q={query}")
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    products_data = data.get("products", [])
                    
                    if not products_data:
                        return None
                    
                    # Converter USD → BRL (taxa reduzida para preços mais acessíveis)
                    products = []
                    for item in products_data:
                        price_brl = item.get("price", 0) * 3.5
                        
                        products.append({
                            "id": str(item.get("id")),
                            "title": item.get("title"),
                            "price": round(price_brl, 2),
                            "currency": "BRL",
                            "thumbnail": item.get("thumbnail"),
                            "link": f"https://dummyjson.com/products/{item.get('id')}",
                            "condition": "new",
                            "available_quantity": item.get("stock", 0)
                        })
                    
                    print(f"[DummyJSON] ✅ {len(products)} produtos")
                    return products
                
                print(f"[DummyJSON] Status {response.status_code}")
                return None
                
        except Exception as e:
            print(f"[DummyJSON] Erro: {str(e)}")
            return None
    
    async def _search_fakestoreapi(self, query: str, limit: int) -> Optional[List[Dict]]:
        """
        FakeStore API - https://fakestoreapi.com/products
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                url = f"{self.apis['fakestoreapi']}/products"
                
                print(f"[FakeStoreAPI] GET {url}")
                response = await client.get(url)
                
                if response.status_code == 200:
                    products_data = response.json()
                    
                    # Filtrar por palavra-chave
                    query_words = query.lower().split()
                    filtered = []
                    
                    for item in products_data:
                        title = item.get("title", "").lower()
                        category = item.get("category", "").lower()
                        description = item.get("description", "").lower()
                        
                        if any(word in title or word in category or word in description for word in query_words):
                            # Taxa reduzida USD→BRL para preços mais baixos
                            price_brl = item.get("price", 0) * 3.5
                            
                            filtered.append({
                                "id": str(item.get("id")),
                                "title": item.get("title"),
                                "price": round(price_brl, 2),
                                "currency": "BRL",
                                "thumbnail": item.get("image"),
                                "link": f"https://fakestoreapi.com/products/{item.get('id')}",
                                "condition": "new",
                                "available_quantity": random.randint(10, 50)
                            })
                    
                    if filtered:
                        print(f"[FakeStoreAPI] ✅ {len(filtered)} produtos")
                        return filtered[:limit]
                    
                    return None
                
                print(f"[FakeStoreAPI] Status {response.status_code}")
                return None
                
        except Exception as e:
            print(f"[FakeStoreAPI] Erro: {str(e)}")
            return None
    
    def _clean_query(self, query: str) -> str:
        """Limpa palavras desnecessárias e traduz termos comuns PT→EN"""
        # Dicionário de traduções PT→EN
        translations = {
            "celular": "phone",
            "smartphone": "phone",
            "telefone": "phone",
            "notebook": "laptop",
            "computador": "laptop computer",
            "pc": "computer",
            "monitor": "monitor",
            "teclado": "keyboard",
            "mouse": "mouse",
            "fone": "headphone",
            "headset": "headphone",
            "relogio": "watch",
            "relógio": "watch",
            "tv": "television",
            "televisao": "television",
            "televisão": "television",
            "camera": "camera",
            "câmera": "camera",
            "tablet": "tablet",
            "console": "console",
            "jogo": "game",
            "sapato": "shoe",
            "tenis": "shoe",
            "tênis": "shoe",
            "roupa": "clothing",
            "camisa": "shirt",
            "calça": "pants",
            "bolsa": "bag",
            "relogio": "watch",
            "oculos": "glasses",
            "óculos": "glasses"
        }
        
        # Palavras a remover (stop words)
        stop_words = [
            "procure", "procurar", "busque", "buscar", "encontre", "encontrar",
            "quero", "preciso", "gostaria", "me", "mostre", "pode", "por", "favor",
            "reais", "real", "r$", "até", "com", "de", "um", "uma"
        ]
        
        # Dividir em palavras
        words = query.lower().split()
        
        # Remover stop words e traduzir
        translated_words = []
        for word in words:
            if word not in stop_words:
                # Se tiver tradução, usar ela
                translated_word = translations.get(word, word)
                translated_words.append(translated_word)
        
        cleaned = " ".join(translated_words).strip()
        print(f"[Query Cleaning] '{query}' → '{cleaned}'")
        return cleaned
    
    def format_products_for_ai(self, products: List[Dict]) -> str:
        """Formata produtos para resposta da IA"""
        if not products:
            return "Nenhum produto encontrado."
        
        result = f"Encontrei {len(products)} produtos:\n\n"
        
        for i, product in enumerate(products, 1):
            price = f"R$ {product['price']:.2f}"
            result += f"{i}. {product['title']}\n"
            result += f"   💰 {price}\n"
            result += f"   🔗 {product['link']}\n\n"
        
        return result
