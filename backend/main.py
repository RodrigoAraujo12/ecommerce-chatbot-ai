from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
from services.ai_service import AIService
from services.product_service import ProductService

load_dotenv()

app = FastAPI(title="E-commerce Support Chatbot API")
ai_service = AIService()
product_service = ProductService()  # Usando APIs públicas: DummyJSON + FakeStoreAPI

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Models
class Message(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]
    store_id: Optional[str] = None


class Product(BaseModel):
    id: str
    title: str
    price: float
    currency: str
    thumbnail: str
    link: str
    condition: Optional[str] = "new"
    available_quantity: Optional[int] = 0


class ChatResponse(BaseModel):
    message: str
    function_called: Optional[str] = None
    products: Optional[List[Product]] = None


# Health check
@app.get("/")
async def root():
    return {"status": "ok", "message": "E-commerce Support Chatbot API"}


# Chat endpoint
@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process chat messages and return AI response with function calling support
    """
    try:
        # Converter mensagens para formato do AI service
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        # Gerar resposta com AI (com suporte a function calling)
        ai_result = await ai_service.generate_response_with_functions(
            messages=messages,
            available_functions={"search_products": product_service.search_products}
        )
        
        # Se a IA decidiu chamar uma função
        if ai_result["type"] == "function_call":
            function_name = ai_result["function"]
            arguments = ai_result["arguments"]
            
            if function_name == "search_products":
                # Buscar produtos
                products = await product_service.search_products(
                    query=arguments.get("query", ""),
                    max_price=arguments.get("max_price")
                )
                
                # Se não encontrou produtos, retornar mensagem amigável
                if not products:
                    return ChatResponse(
                        message="Desculpe, não encontrei produtos com esse termo. Tente buscar com palavras-chave mais específicas como 'celular', 'notebook', 'monitor', etc.",
                        function_called="search_products",
                        products=[]
                    )
                
                # Formatar resposta em texto
                formatted_response = product_service.format_products_for_ai(products)
                
                return ChatResponse(
                    message=formatted_response,
                    function_called="search_products",
                    products=products  # Enviar produtos estruturados para o frontend
                )
        
        # Resposta normal (texto)
        return ChatResponse(
            message=ai_result["content"],
            function_called=None
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# E-commerce API integrations placeholder
@app.get("/api/orders/{order_id}")
async def get_order(order_id: str):
    """
    Get order details from e-commerce platform
    """
    # TODO: Implement integration with Shopify/WooCommerce/etc
    return {"order_id": order_id, "status": "pending", "message": "Integration coming soon"}


@app.get("/api/products/search")
async def search_products(query: str):
    """
    Search products in e-commerce platform
    """
    # TODO: Implement product search
    return {"query": query, "results": [], "message": "Integration coming soon"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
