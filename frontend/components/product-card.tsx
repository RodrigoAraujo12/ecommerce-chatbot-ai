"use client";

import { ExternalLink, ShoppingCart } from "lucide-react";
import Image from "next/image";

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

type ProductCardProps = {
  product: Product;
};

export default function ProductCard({ product }: ProductCardProps) {
  return (
    <div className="group relative bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
      {/* Badge de Condição */}
      {product.condition === "new" && (
        <div className="absolute top-3 left-3 z-10 bg-green-500 text-white text-xs font-bold px-3 py-1 rounded-full">
          NOVO
        </div>
      )}
      
      {/* Imagem do Produto */}
      <div className="relative h-48 bg-gray-50 dark:bg-gray-900 overflow-hidden">
        <img
          src={product.thumbnail}
          alt={product.title}
          className="w-full h-full object-contain p-4 group-hover:scale-110 transition-transform duration-300"
        />
      </div>

      {/* Conteúdo */}
      <div className="p-4 space-y-3">
        {/* Título */}
        <h3 className="font-semibold text-gray-900 dark:text-gray-100 line-clamp-2 min-h-[3rem] text-sm leading-tight">
          {product.title}
        </h3>

        {/* Preço */}
        <div className="flex items-baseline gap-2">
          <span className="text-2xl font-bold text-blue-600 dark:text-blue-400">
            R$ {product.price.toFixed(2)}
          </span>
          {product.available_quantity && product.available_quantity > 0 && (
            <span className="text-xs text-green-600 dark:text-green-400 font-medium">
              {product.available_quantity} em estoque
            </span>
          )}
        </div>

        {/* Botão */}
        <a
          href={product.link}
          target="_blank"
          rel="noopener noreferrer"
          className="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-blue-500 to-indigo-600 dark:from-blue-600 dark:to-indigo-700 text-white py-2.5 px-4 rounded-lg hover:from-blue-600 hover:to-indigo-700 dark:hover:from-blue-700 dark:hover:to-indigo-800 transition-all duration-200 font-medium text-sm group/button"
        >
          <ShoppingCart className="w-4 h-4" />
          Ver Produto
          <ExternalLink className="w-3 h-3 opacity-0 group-hover/button:opacity-100 transition-opacity" />
        </a>
      </div>
    </div>
  );
}
