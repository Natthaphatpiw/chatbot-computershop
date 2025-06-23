"use client"

import React, { useState } from "react"
import Image from "next/image"
import type { Product } from "@/types"
import { ShoppingCart, Heart, Star, Cpu, HardDrive, Monitor, Gamepad, Eye, ChevronLeft, ChevronRight } from "lucide-react"
import { motion } from "framer-motion"
import { ProductModal } from "./ProductModal"

interface ProductCardProps {
  product: Product
}

export function ProductCard({ product }: ProductCardProps) {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isWishlisted, setIsWishlisted] = useState(false)
  const [currentImageIndex, setCurrentImageIndex] = useState(0)
  
  const images = product.images?.medium?.url || []
  const discount = product.price - product.salePrice
  const discountPercent = discount > 0 ? Math.round((discount / product.price) * 100) : 0
  const hasDiscount = discount > 0

  const handleWishlist = (e: React.MouseEvent) => {
    e.stopPropagation()
    setIsWishlisted(!isWishlisted)
  }

  const nextImage = (e: React.MouseEvent) => {
    e.stopPropagation()
    setCurrentImageIndex((prev: number) => (prev + 1) % images.length)
  }

  const prevImage = (e: React.MouseEvent) => {
    e.stopPropagation()
    setCurrentImageIndex((prev: number) => (prev - 1 + images.length) % images.length)
  }

  // Helper function to get appropriate icon based on category
  const getCategoryIcon = () => {
    const categoryName = product.navigation?.categoryMessage1 || ""
    if (categoryName.includes("โน้ตบุ๊ก") || categoryName.includes("laptop")) {
      return <Cpu size={12} />
    } else if (categoryName.includes("คอมพิวเตอร์") || categoryName.includes("desktop")) {
      return <Monitor size={12} />
    } else if (categoryName.includes("เกม") || categoryName.includes("gaming")) {
      return <Gamepad size={12} />
    } else if (categoryName.includes("จัดเก็บ") || categoryName.includes("storage")) {
      return <HardDrive size={12} />
    } else {
      return <Cpu size={12} />
    }
  }

  const getCategoryDisplay = () => {
    return product.navigation?.categoryMessage2 || product.navigation?.categoryMessage1 || "สินค้าไอที"
  }
  
  return (
    <>
      <motion.div 
        className="card-hover bg-white dark:bg-gray-800 rounded-xl overflow-hidden border border-gray-100 dark:border-gray-700 cursor-pointer group h-full flex flex-col"
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.3 }}
        onClick={() => setIsModalOpen(true)}
      >
        <div className="relative h-40 w-full">
          <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-b from-transparent to-black/20 z-10 group-hover:opacity-70 transition-all duration-300" />
          
          <Image
            src={images[currentImageIndex] || "https://via.placeholder.com/300x200?text=IT+Equipment"}
            alt={product.title}
            fill
            className="object-cover transition-transform duration-700 group-hover:scale-105"
          />
          
          {/* Image navigation arrows */}
          {images.length > 1 && (
            <>
              <button 
                className="absolute left-2 top-1/2 -translate-y-1/2 z-20 p-1 rounded-full bg-black/50 text-white hover:bg-black/70 transition-all opacity-0 group-hover:opacity-100"
                onClick={prevImage}
              >
                <ChevronLeft size={16} />
              </button>
              <button 
                className="absolute right-2 top-1/2 -translate-y-1/2 z-20 p-1 rounded-full bg-black/50 text-white hover:bg-black/70 transition-all opacity-0 group-hover:opacity-100"
                onClick={nextImage}
              >
                <ChevronRight size={16} />
              </button>
              
              {/* Image indicators */}
              <div className="absolute bottom-2 left-1/2 -translate-x-1/2 z-20 flex gap-1">
                {images.map((_, index) => (
                  <button
                    key={index}
                    className={`w-2 h-2 rounded-full transition-all ${
                      index === currentImageIndex ? 'bg-white' : 'bg-white/50'
                    }`}
                    onClick={(e: React.MouseEvent) => {
                      e.stopPropagation()
                      setCurrentImageIndex(index)
                    }}
                  />
                ))}
              </div>
            </>
          )}

          <button 
            className={`absolute top-3 right-3 z-20 p-2 rounded-full backdrop-blur-sm transition-all ${
              isWishlisted 
                ? "bg-red-500/90 text-white" 
                : "bg-white/80 dark:bg-gray-800/80 text-gray-600 dark:text-gray-400 hover:text-red-500"
            }`}
            onClick={handleWishlist}
          >
            <Heart size={16} className={isWishlisted ? "fill-current" : ""} />
          </button>
          
          {/* Discount badge */}
          {hasDiscount && (
            <div className="absolute top-3 left-3 z-20 bg-red-500/90 text-white px-2 py-1 rounded-md text-xs font-medium backdrop-blur-sm">
              -{discountPercent}%
            </div>
          )}
          
          {product.stockQuantity === 0 && (
            <div className="absolute bottom-0 left-0 right-0 bg-black/70 text-white py-2 text-center text-sm font-medium z-20">
              สินค้าหมด
            </div>
          )}
          
          {product.rating >= 4.5 && (
            <div className="absolute bottom-3 left-3 z-20 bg-yellow-400/90 text-yellow-900 px-2 py-1 rounded-md text-xs font-medium flex items-center gap-1 backdrop-blur-sm">
              <Star size={12} fill="currentColor" /> สินค้าขายดี
            </div>
          )}
        </div>

        <div className="p-3 flex flex-col flex-grow">
          <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400 mb-2">
            <span className="capitalize bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 px-2 py-0.5 rounded-full flex items-center gap-1">
              {getCategoryIcon()}
              {getCategoryDisplay()}
            </span>
            
            {/* Popularity indicator */}
            <div className="flex items-center gap-1 text-gray-400">
              <Eye size={12} />
              <span>{product.productView.toLocaleString()}</span>
            </div>
          </div>
          
          <h3 className="font-bold text-sm text-gray-900 dark:text-gray-100 mb-1 line-clamp-2 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors leading-tight">
            {product.title}
          </h3>

          <p className="text-xs text-gray-600 dark:text-gray-300 mb-2 line-clamp-2 flex-grow">
            {product.description}
          </p>

          {/* Price section */}
          <div className="flex items-center justify-between mb-2">
            <div className="flex flex-col">
              {hasDiscount && (
                <span className="text-xs text-gray-400 line-through">
                  ฿{product.price.toLocaleString()}
                </span>
              )}
              <span className="text-sm font-bold text-blue-600 dark:text-blue-400">
                ฿{product.salePrice.toLocaleString()}
              </span>
            </div>

            <div className="flex items-center bg-gray-50 dark:bg-gray-700 px-1.5 py-0.5 rounded-lg">
              <Star size={12} className="text-yellow-400 fill-current" />
              <span className="text-xs text-gray-600 dark:text-gray-300 ml-1">{product.rating}</span>
            </div>
          </div>

          <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400 mb-2">
            <div className="flex items-center gap-1">
              <HardDrive size={12} />
              <span>คงเหลือ: {product.stockQuantity}</span>
            </div>
            <div className="flex items-center gap-1">
              <Star size={12} />
              <span>รีวิว: {product.totalReviews}</span>
            </div>
          </div>

          <button
            className={`w-full py-2 px-3 rounded-lg flex items-center justify-center gap-1.5 transition-all duration-300 text-xs ${
              product.stockQuantity > 0
                ? "bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 text-white shadow-sm hover:shadow-md" 
                : "bg-gray-100 dark:bg-gray-700 text-gray-400 dark:text-gray-500 cursor-not-allowed"
            }`}
            disabled={product.stockQuantity === 0}
            onClick={(e: React.MouseEvent) => {
              e.stopPropagation()
              // Add to cart functionality would go here
            }}
          >
            {product.stockQuantity > 0 ? (
              <>
                <ShoppingCart size={14} />
                เพิ่มลงตะกร้า
              </>
            ) : (
              <>
                สินค้าหมด
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