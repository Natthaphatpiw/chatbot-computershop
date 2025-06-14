"use client"

import { useState } from "react"
import Image from "next/image"
import type { Product } from "@/types"
import { ShoppingCart, Heart, Star, Check } from "lucide-react"
import { motion } from "framer-motion"
import { ProductModal } from "./ProductModal"

interface ProductCardProps {
  product: Product
}

export function ProductCard({ product }: ProductCardProps) {
  // Default rating to 0 if undefined
  const rating = product.rating ?? 0;
  const [isModalOpen, setIsModalOpen] = useState(false);
  
  return (
    <>
      <motion.div 
        className="bg-white dark:bg-gray-800 rounded-xl shadow-md hover:shadow-lg transition-all duration-300 overflow-hidden border border-gray-100 dark:border-gray-700 cursor-pointer group"
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.3 }}
        whileHover={{ y: -4 }}
        onClick={() => setIsModalOpen(true)}
      >
        <div className="relative h-52 w-full">
          <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-b from-transparent to-black/10 z-10 group-hover:from-transparent group-hover:to-black/20 transition-all duration-300" />
          
          <Image
            src={product.image_url || "/placeholder.svg?height=200&width=300"}
            alt={product.name}
            fill
            className="object-cover"
          />
          
          <button 
            className="absolute top-3 right-3 z-20 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm p-1.5 rounded-full hover:bg-white dark:hover:bg-gray-700 transition-colors"
            onClick={(e) => {
              e.stopPropagation();
              // Add to wishlist functionality would go here
            }}
          >
            <Heart size={18} className="text-gray-600 dark:text-gray-400 hover:text-red-500 transition-colors" />
          </button>
          
          {!product.inStock && (
            <div className="absolute top-3 left-3 z-20 bg-red-500 text-white px-2 py-1 rounded-md text-xs font-medium">
              Out of Stock
            </div>
          )}
          
          {product.rating && product.rating >= 4.5 && (
            <div className="absolute bottom-3 left-3 z-20 bg-yellow-400 text-yellow-900 px-2 py-1 rounded-md text-xs font-medium flex items-center gap-1">
              <Star size={12} fill="currentColor" /> Top Rated
            </div>
          )}
        </div>

        <div className="p-4">
          <div className="flex items-center text-xs text-gray-500 dark:text-gray-400 mb-2">
            <span className="capitalize bg-gray-100 dark:bg-gray-700 px-2 py-0.5 rounded-full">{product.category}</span>
          </div>
          
          <h3 className="font-bold text-lg text-gray-900 dark:text-gray-100 mb-1 line-clamp-2">{product.name}</h3>

          <p className="text-gray-600 dark:text-gray-300 text-sm mb-3 line-clamp-2">{product.description}</p>

          <div className="flex items-center justify-between mb-3">
            <span className="text-xl font-bold text-blue-600 dark:text-blue-400">฿{product.price.toFixed(2)}</span>

            {product.rating && (
              <div className="flex items-center bg-gray-50 dark:bg-gray-700 px-2 py-0.5 rounded-lg">
                {[...Array(5)].map((_, i) => (
                  <Star 
                    key={i} 
                    size={14} 
                    className={i < Math.floor(rating) ? "text-yellow-400" : "text-gray-300 dark:text-gray-600"}
                    fill={i < Math.floor(rating) ? "currentColor" : "none"}
                  />
                ))}
                <span className="text-xs text-gray-600 dark:text-gray-300 ml-1">{rating}</span>
              </div>
            )}
          </div>

          <button
            className={`w-full py-2.5 px-4 rounded-lg flex items-center justify-center gap-2 transition-colors duration-200 ${
              product.inStock 
                ? "bg-blue-600 hover:bg-blue-700 text-white" 
                : "bg-gray-100 dark:bg-gray-700 text-gray-400 dark:text-gray-500 cursor-not-allowed"
            }`}
            disabled={!product.inStock}
            onClick={(e) => {
              e.stopPropagation();
              // Add to cart functionality would go here
            }}
          >
            {product.inStock ? (
              <>
                <ShoppingCart size={16} />
                Add to Cart
              </>
            ) : (
              <>
                Out of Stock
              </>
            )}
          </button>
        </div>
      </motion.div>

      {/* Product Modal */}
      <ProductModal 
        product={product} 
        isOpen={isModalOpen} 
        onClose={() => setIsModalOpen(false)} 
      />
    </>
  )
}
