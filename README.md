# E-commerce Support Chatbot 🤖

Assistente de atendimento inteligente para e-commerce com IA, RAG e busca de produtos em tempo real.

## ✨ Funcionalidades

- 🤖 **Chat conversacional** com Google Gemini AI (temperatura 0.2 para precisão)
- 📚 **RAG (Retrieval Augmented Generation)** com ChromaDB para perguntas técnicas
- 🛍️ **Busca inteligente de produtos** em APIs públicas (DummyJSON, FakeStoreAPI)
- 🎨 **Interface moderna** com glassmorphism, dark mode e animações
- 💬 **Chips de sugestões** para facilitar interação
- 🌐 **Detecção de intenção** conversacional (não apenas keywords)
- 🇧🇷 **Suporte em português** com tradução automática de termos
- 📱 **Totalmente responsiva** para mobile, tablet e desktop
- 🎯 **Cards de produtos** modernos com imagens, preços e links

## 🚀 Tech Stack

### Backend
- **FastAPI** - Framework Python assíncrono
- **Python 3.13.11** com type hints
- **Google Gemini API** (gemini-2.5-flash) - IA conversacional
- **ChromaDB** - Vector database para RAG
- **Sentence Transformers** - Embeddings multilíngues (paraphrase-multilingual-MiniLM-L12-v2)
- **HTTPX** - Cliente HTTP assíncrono
- **DummyJSON & FakeStoreAPI** - APIs públicas de produtos

### Frontend
- **Next.js 15** - React framework com App Router
- **TypeScript** - Tipagem estática completa
- **Tailwind CSS** - Estilização utility-first com dark mode
- **Shadcn/ui** - Componentes UI modernos e acessíveis
- **Lucide Icons** - Ícones SVG otimizados

### IA & RAG
- **Google Gemini 2.5 Flash** - Modelo de linguagem
- **ChromaDB** - Armazenamento vetorial
- **Sentence Transformers** - Geração de embeddings
- **Vector Similarity Search** - Busca semântica de contexto

## 📁 Estrutura do Projeto

```
Sistema Novo/
├── backend/
│   ├── main.py                    # API FastAPI principal
│   ├── requirements.txt           # Dependências Python
│   ├── .env.example              # Variáveis de ambiente
│   ├── data/
│   │   ├── manual_tecnico.txt    # Base de conhecimento para RAG
│   │   └── chroma_db/            # Vector database (auto-gerado)
│   └── services/
│       ├── ai_service.py         # Integração com Gemini AI
│       ├── product_service.py    # Integração com APIs públicas
│       └── rag_service.py        # RAG com ChromaDB
│
├── frontend/
│   ├── app/
│   │   ├── layout.tsx            # Layout principal
│   │   ├── page.tsx              # Página inicial
│   │   └── globals.css           # Estilos globais + Tailwind
│   ├── components/
│   │   ├── chat-interface.tsx   # Interface do chat
│   │   ├── product-card.tsx     # Card de produto
│   │   └── ui/                   # Componentes Shadcn
│   ├── package.json
│   └── tsconfig.json
│
└── README.md
```

## 🎯 Como Fun3+**
- **Node.js 18+** e npm/yarn/pnpm
- Conta no **Google AI Studio** (para Gemini API key - gratuita
O Gemini analisa a mensagem e decide:
- **Pergunta técnica?** → Usa RAG (consulta manual técnico)
- **Busca de produto?** → Chama APIs de produtos
- **Conversa normal?** → Resposta conversacional

### 2. RAG (Retrieval Augmented Generation)
- Manual técnico dividido em chunks
- Embeddings gerados com modelo multilíngue
- ChromaDB faz busca vetorial (similaridade)
- Top 3 trechos mais relevantes vão pro Gemini
- Resposta baseada em conhecimento real

### 3. Busca de Produtos
- Extração inteligente de parâmetros (produto, preço máximo)
- Tradução PT→EN automática
- Busca em múltiplas APIs (DummyJSON + FakeStore)
- Conversão de moeda USD→BRL
- Fallback para termos genéricos

## 🛠️ Instalação

### Pré-requisitos
- **Python 3.10+**
- **Node.js 18+** e npm/yarn/pnpm
- Conta na **OpenAI** ou **Anthropic** (para API key)

### 1️⃣ Backend (FastAPI)

```bash
# Navegar para a pasta do backend
cd backend

# Criar ambiente virtual (recomendado)
python -m venv venv

# Ativar ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Editar .env e adicionar suas API keys

# Rodar o servidor
python main.py
# Ou com uvicorn:
uvicorn main:app --reload
```

Backend rodando em: **http://localhost:8000**

### 2️⃣ Frontend (Next.js)

```bash
# Navegar para a pasta do frontend
cd frontend

# Instalar dependências
npm install
# ou
yarn install
# ou
pnpm install

# Configurar variáveis de ambiente (opcional)
cp .env.example .env.local

# Rodar o servidor de desenvolvimento
npm run dev
# ou
yarn dev
# ou
pnpm dev
```

Frontend rodando em: **http://localhost:3000**

## 🔑 Configuração de API Keys

### Google Gemini (Gratuito!)
1. Acesse https://aistudio.google.com/app/apikey
2. Crie uma API key
3. Adicione no `backend/.env`:
```env
GEMINI_API_KEY=your_key_here
```

**Limites do plano gratuito:**
- 20 requisições por minuto
- 1500 requisições por dia
- Suficiente para desenvolvimento e testes!

## 📝 Como Usar

1. **Inicie o backend** (terminal 1):
```bash
cd backend
python main.py
```

2. **Inicie o frontend** (terminal 2):
```bash
cd frontend
npm run dev
```

3. **Acesse** http://localhost:3000

4. **Converse** com o chatbot!

## 🎨 Próximos Passos

### Implementações Pendentes

- [ ] Integrar OpenAI API no backend (`ai_service.py`)
- [ ] Implementar Function Calling para chamadas de API
- [ ] Conectar com APIs de e-commerce (Shopify, WooCommerce)
- [ ] Adicionar autenticação de usuários
- [ ] Features Implementadas

### ✅ Concluído
- [x] Chat conversacional com Gemini AI
- [x] RAG com ChromaDB e embeddings multilíngues
- [x] Busca inteligente de produtos
- [x] Detecção de intenção conversacional
- [x] Extração automática de parâmetros (produto, preço)
- [x] Interface com glassmorphism e dark mode
- [x] Chips de sugestões interativos
- [x] Cards de produtos modernos
- [x] Animações e transições suaves
- [x] Timestamps nas mensagens
- [x] Auto-scroll do chat
- [x] Temperatura otimizada (0.2) para precisão
- [x] Tradução PT→EN automática
- [x] Fallback de busca (específico → genérico)
- [x] Tratamento de erros robusto

### 🚧 Próximos Passos (Opcionais)
- [ ] Deploy (Vercel + Railway)
- [ ] Histórico de conversas (localStorage)
- [ ] Testes automatizados
- [ ] Analytics básico
- [ ] Rate limiting
- [ ] Múltiplas conversas (tabs)
- [ ] Export de conversas (PDF/TXT) - use como quiser!

## 📧 Contato

Dúvidas? Abra uma issue ou entre em contato.

---

**Feito com ❤️ usando as tecnologias mais modernas**
Contribuições são bem-vindas! Sinta-se à vontade para:
- Reportar bugs
- Sugerir features
- Enviar pull requests

## 📄 Licença

MIT License - use como quiser!

## 🙏 Agradecimentos

- Google Gemini API
- ChromaDB
- Shadcn/ui
- DummyJSON & FakeStoreAPI

---

**Desenvolvido com ❤️ usando as melhores tecnologias do mercado**