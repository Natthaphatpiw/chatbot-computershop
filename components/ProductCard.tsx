"use client"

import { useState } from "react"
import Image from "next/image"
import type { Product } from "@/types"
import { ShoppingCart, Heart, Star, Check, Tag, Clock, Truck, Shield } from "lucide-react"
import { motion } from "framer-motion"
import { ProductModal } from "./ProductModal"

interface ProductCardProps {
  product: Product
}

export function ProductCard({ product }: ProductCardProps) {
  // Default rating to 0 if undefined
  const rating = product.rating ?? 0;
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isWishlisted, setIsWishlisted] = useState(false);
  
  const handleWishlist = (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsWishlisted(!isWishlisted);
  };
  
  return (
    <>
      <motion.div 
        className="card-hover bg-white dark:bg-gray-800 rounded-xl overflow-hidden border border-gray-100 dark:border-gray-700 cursor-pointer group"
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.3 }}
        onClick={() => setIsModalOpen(true)}
      >
        <div className="relative h-52 w-full">
          <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-b from-transparent to-black/20 z-10 group-hover:opacity-70 transition-all duration-300" />
          
          <Image
            src={product.image_url || "/placeholder.svg?height=200&width=300"}
            alt={product.name}
            fill
            className="object-cover transition-transform duration-700 group-hover:scale-105"
          />
          
          <button 
            className={`absolute top-3 right-3 z-20 p-2 rounded-full backdrop-blur-sm transition-all ${
              isWishlisted 
                ? "bg-red-500/90 text-white" 
                : "bg-white/80 dark:bg-gray-800/80 text-gray-600 dark:text-gray-400 hover:text-red-500"
            }`}
            onClick={handleWishlist}
          >
            <Heart size={18} className={isWishlisted ? "fill-current" : ""} />
          </button>
          
          {product.discount && (
            <div className="absolute top-3 left-3 z-20 bg-red-500 text-white px-2 py-1 rounded-md text-xs font-medium flex items-center gap-1">
              <Tag size={12} /> -{product.discount}%
            </div>
          )}
          
          {!product.inStock && (
            <div className="absolute bottom-0 left-0 right-0 bg-black/70 text-white py-2 text-center text-sm font-medium z-20">
              สินค้าหมด
            </div>
          )}
          
          {product.rating && product.rating >= 4.5 && (
            <div className="absolute bottom-3 left-3 z-20 bg-yellow-400/90 text-yellow-900 px-2 py-1 rounded-md text-xs font-medium flex items-center gap-1 backdrop-blur-sm">
              <Star size={12} fill="currentColor" /> สินค้าขายดี
            </div>
          )}
        </div>

        <div className="p-4">
          <div className="flex items-center text-xs text-gray-500 dark:text-gray-400 mb-2 gap-2">
            <span className="capitalize bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 px-2 py-0.5 rounded-full">{product.category}</span>
            {product.freeShipping && (
              <span className="bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400 px-2 py-0.5 rounded-full flex items-center gap-1">
                <Truck size={10} /> ส่งฟรี
              </span>
            )}
          </div>
          
          <h3 className="font-bold text-lg text-gray-900 dark:text-gray-100 mb-1 line-clamp-2 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">{product.name}</h3>

          <p className="text-gray-600 dark:text-gray-300 text-sm mb-3 line-clamp-2">{product.description}</p>

          <div className="flex items-center justify-between mb-3">
            <div className="flex flex-col">
              {product.originalPrice && product.originalPrice > product.price ? (
                <>
                  <span className="text-xl font-bold text-blue-600 dark:text-blue-400">฿{product.price.toLocaleString()}</span>
                  <span className="text-sm text-gray-500 line-through">฿{product.originalPrice.toLocaleString()}</span>
                </>
              ) : (
                <span className="text-xl font-bold text-blue-600 dark:text-blue-400">฿{product.price.toLocaleString()}</span>
              )}
            </div>

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
            className={`w-full py-2.5 px-4 rounded-lg flex items-center justify-center gap-2 transition-all duration-300 ${
              product.inStock 
                ? "bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 text-white shadow-sm hover:shadow-md" 
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
                เพิ่มลงตะกร้า
              </>
            ) : (
              <>
                สินค้าหมด
              </>
            )}
          </button>
          
          <div className="mt-3 flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
            {product.fastDelivery && (
              <div className="flex items-center gap-1">
                <Truck size={12} />
                <span>จัดส่งด่วน</span>
              </div>
            )}
            {product.warranty && (
              <div className="flex items-center gap-1">
                <Shield size={12} />
                <span>รับประกัน {product.warranty}</span>
              </div>
            )}
          </div>
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
