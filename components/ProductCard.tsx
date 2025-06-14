"use client"

import { useState } from "react"
import Image from "next/image"
import type { Product } from "@/types"
import { ShoppingCart, Heart, Star, Cpu, HardDrive, Monitor, Gamepad } from "lucide-react"
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

  // Helper function to get appropriate icon based on category
  const getCategoryIcon = () => {
    switch(product.category) {
      case "โน้ตบุ๊ค":
        return <Cpu size={12} />;
      case "คอมพิวเตอร์ตั้งโต๊ะ":
        return <Monitor size={12} />;
      case "อุปกรณ์เสริม":
        return <HardDrive size={12} />;
      case "จัดเก็บข้อมูล":
        return <HardDrive size={12} />;
      case "เกมมิ่งเกียร์":
        return <Gamepad size={12} />;
      default:
        return <Cpu size={12} />;
    }
  };
  
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
            src={product.image_url || "https://via.placeholder.com/300x200?text=IT+Equipment"}
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
            <Heart size={16} className={isWishlisted ? "fill-current" : ""} />
          </button>
          
          {product.stock === 0 && (
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

        <div className="p-3 flex flex-col flex-grow">
          <div className="flex items-center text-xs text-gray-500 dark:text-gray-400 mb-2 gap-2">
            <span className="capitalize bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 px-2 py-0.5 rounded-full flex items-center gap-1">
              {getCategoryIcon()}
              {product.category}
            </span>
          </div>
          
          <h3 className="font-bold text-sm text-gray-900 dark:text-gray-100 mb-1 line-clamp-1 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">{product.name}</h3>

          <p className="text-xs text-gray-600 dark:text-gray-300 mb-2 line-clamp-2 flex-grow">{product.description}</p>

          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-bold text-blue-600 dark:text-blue-400">฿{product.price.toLocaleString()}</span>

            {product.rating && (
              <div className="flex items-center bg-gray-50 dark:bg-gray-700 px-1.5 py-0.5 rounded-lg">
                <Star size={12} className="text-yellow-400 fill-current" />
                <span className="text-xs text-gray-600 dark:text-gray-300 ml-1">{rating}</span>
              </div>
            )}
          </div>

          <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400 mb-2">
            <div className="flex items-center gap-1">
              <HardDrive size={12} />
              <span>สต็อก: {product.stock}</span>
            </div>
            {product.reviews && (
              <div className="flex items-center gap-1">
                <Star size={12} />
                <span>รีวิว: {product.reviews}</span>
              </div>
            )}
          </div>

          <button
            className={`w-full py-2 px-3 rounded-lg flex items-center justify-center gap-1.5 transition-all duration-300 text-xs ${
              product.stock > 0
                ? "bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 text-white shadow-sm hover:shadow-md" 
                : "bg-gray-100 dark:bg-gray-700 text-gray-400 dark:text-gray-500 cursor-not-allowed"
            }`}
            disabled={product.stock === 0}
            onClick={(e) => {
              e.stopPropagation();
              // Add to cart functionality would go here
            }}
          >
            {product.stock > 0 ? (
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
