"use client";

import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Send, Bot, User, Moon, Sun, Sparkles } from "lucide-react";
import ProductCard from "./product-card";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

type Product = {
  id: string;
  title: string;
  price: number;
  currency: string;
  thumbnail: string;
  link: string;
  condition?: string;
  available_quantity?: number;
};

type Message = {
  role: "user" | "assistant";
  content: string;
  products?: Product[];
  timestamp?: Date;
};

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "Olá! Como posso ajudá-lo hoje? Posso auxiliar com pedidos, produtos e informações sobre a loja.",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [mounted, setMounted] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const suggestions = [
    { icon: "📱", text: "Buscar smartphones" },
    { icon: "💻", text: "Ver notebooks" },
    { icon: "🔍", text: "Diferença SSD vs HDD" },
    { icon: "💾", text: "Quanto de RAM preciso?" },
  ];

  const handleSuggestionClick = (text: string) => {
    setInput(text);
    setShowSuggestions(false);
  };

  // Montar componente (evita hidratação)
  useEffect(() => {
    setMounted(true);
  }, []);

  // Carregar preferência de dark mode do localStorage
  useEffect(() => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
      setIsDarkMode(true);
      document.documentElement.classList.add('dark');
    }
  }, []);

  // Toggle dark mode
  const toggleDarkMode = () => {
    const newMode = !isDarkMode;
    setIsDarkMode(newMode);
    if (newMode) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  };

  // Scroll automático para última mensagem
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    setShowSuggestions(false);
    const userMessage: Message = { 
      role: "user", 
      content: input,
      timestamp: new Date()
    };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      // TODO: Replace with actual API call to backend
      const response = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          messages: [...messages, userMessage],
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to get response");
      }

      const data = await response.json();
      const assistantMessage: Message = {
        role: "assistant",
        content: data.message,
        products: data.products || undefined,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error("Error:", error);
      const errorMessage: Message = {
        role: "assistant",
        content: "Desculpe, ocorreu um erro. Por favor, tente novamente. (Certifique-se de que o backend está rodando)",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <Card className="w-full shadow-2xl backdrop-blur-xl bg-white/80 dark:bg-gray-900/80 border border-white/20 dark:border-gray-700/50 transition-all duration-300">
      <CardHeader className="bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-600 dark:from-blue-600 dark:via-indigo-600 dark:to-purple-700 text-white relative">
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Bot className="w-6 h-6" />
            Assistente Virtual
          </div>
          <Button
            onClick={toggleDarkMode}
            variant="ghost"
            size="icon"
            className="hover:bg-white/20 transition-colors rounded-full"
          >
            {isDarkMode ? (
              <Sun className="w-5 h-5 text-yellow-300" />
            ) : (
              <Moon className="w-5 h-5 text-white" />
            )}
          </Button>
        </CardTitle>
      </CardHeader>
      <CardContent className="h-[600px] overflow-y-auto p-4 space-y-4 bg-gradient-to-b from-gray-50 to-white dark:from-gray-800 dark:to-gray-900 transition-colors duration-300">
        {messages.map((message, index) => (
          <div key={index} className="space-y-3 animate-in fade-in slide-in-from-bottom-2 duration-500">
            <div
              className={`flex gap-3 ${
                message.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              {message.role === "assistant" && (
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center flex-shrink-0 shadow-md">
                  <Bot className="w-5 h-5 text-white" />
                </div>
              )}
              <div className="flex flex-col gap-1 max-w-[70%]">
                <div
                  className={`rounded-2xl p-4 shadow-sm transition-colors duration-300 ${
                    message.role === "user"
                      ? "bg-gradient-to-br from-blue-500 to-indigo-600 text-white rounded-tr-none"
                      : "bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 border border-gray-200 dark:border-gray-600 rounded-tl-none"
                  }`}
                >
                  <div className="prose prose-sm dark:prose-invert max-w-none 
                    prose-p:my-1 prose-p:leading-relaxed
                    prose-headings:my-2 prose-headings:font-semibold
                    prose-ul:my-2 prose-ul:pl-4 
                    prose-ol:my-2 prose-ol:pl-4
                    prose-li:my-0.5
                    prose-strong:font-bold prose-strong:text-inherit
                    prose-code:bg-gray-100 prose-code:dark:bg-gray-700 prose-code:px-1 prose-code:py-0.5 prose-code:rounded prose-code:text-sm
                    prose-a:text-blue-500 prose-a:no-underline hover:prose-a:underline">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {message.content}
                    </ReactMarkdown>
                  </div>
                </div>
                {mounted && message.timestamp && (
                  <span className={`text-xs text-gray-400 dark:text-gray-500 px-2 ${
                    message.role === "user" ? "text-right" : "text-left"
                  }`} suppressHydrationWarning>
                    {message.timestamp.toLocaleTimeString('pt-BR', { 
                      hour: '2-digit', 
                      minute: '2-digit' 
                    })}
                  </span>
                )}
              </div>
              {message.role === "user" && (
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-gray-700 to-gray-900 flex items-center justify-center flex-shrink-0 shadow-md">
                  <User className="w-5 h-5 text-white" />
                </div>
              )}
            </div>
            
            {/* Grid de Cards de Produtos */}
            {message.products && message.products.length > 0 && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-4 ml-11 animate-in fade-in slide-in-from-bottom-4 duration-700">
                {message.products.map((product) => (
                  <ProductCard key={product.id} product={product} />
                ))}
              </div>
            )}
          </div>
        ))}
        {isLoading && (
          <div className="flex gap-3 justify-start animate-in fade-in slide-in-from-bottom-2 duration-300">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center flex-shrink-0 shadow-md">
              <Bot className="w-5 h-5 text-white" />
            </div>
            <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-2xl rounded-tl-none p-4 shadow-sm transition-colors duration-300">
              <div className="flex gap-1.5">
                <div className="w-2.5 h-2.5 bg-blue-400 rounded-full animate-bounce [animation-delay:-0.3s]" />
                <div className="w-2.5 h-2.5 bg-blue-500 rounded-full animate-bounce [animation-delay:-0.15s]" />
                <div className="w-2.5 h-2.5 bg-blue-600 rounded-full animate-bounce" />
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </CardContent>
      <CardFooter className="border-t backdrop-blur-md bg-white/90 dark:bg-gray-800/90 dark:border-gray-700 p-4 transition-colors duration-300">
        {showSuggestions && messages.length === 1 && (
          <div className="flex flex-wrap gap-2 mb-3 w-full">
            {suggestions.map((suggestion, index) => (
              <button
                key={index}
                onClick={() => handleSuggestionClick(suggestion.text)}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-gray-700 dark:to-gray-600 hover:from-blue-100 hover:to-indigo-100 dark:hover:from-gray-600 dark:hover:to-gray-500 text-sm font-medium text-gray-700 dark:text-gray-200 transition-all duration-200 hover:shadow-md border border-blue-200 dark:border-gray-600"
              >
                <span>{suggestion.icon}</span>
                <span>{suggestion.text}</span>
              </button>
            ))}
          </div>
        )}
        <div className="flex gap-2 w-full">
          <Input
            placeholder="Digite sua mensagem..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={isLoading}
            className="flex-1 border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 dark:focus:ring-blue-500 rounded-xl transition-colors duration-300"
          />
          <Button
            onClick={handleSend}
            disabled={isLoading || !input.trim()}
            className="bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 text-white shadow-md hover:shadow-lg transition-all duration-200 rounded-xl px-6"
          >
            <Send className="w-4 h-4" />
          </Button>
        </div>
      </CardFooter>
    </Card>
  );
}
