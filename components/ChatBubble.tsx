import type { ChatMessage } from "@/types"
import { ProductCard } from "./ProductCard"
import { User, Bot, Copy, Check, ChevronDown, Clock, ChevronRight, ChevronLeft } from "lucide-react"
import { motion } from "framer-motion"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import { useState, useRef } from "react"

interface ChatBubbleProps {
  message: ChatMessage
}

export function ChatBubble({ message }: ChatBubbleProps) {
  const isUser = message.role === "user"
  const [copied, setCopied] = useState(false)
  const [showAllProducts, setShowAllProducts] = useState(false)
  const scrollContainerRef = useRef<HTMLDivElement>(null)
  const productsToShow = showAllProducts ? message.products : message.products?.slice(0, 6)
  
  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  
  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  };

  const scrollLeft = () => {
    if (scrollContainerRef.current) {
      scrollContainerRef.current.scrollBy({ left: -300, behavior: 'smooth' });
    }
  };

  const scrollRight = () => {
    if (scrollContainerRef.current) {
      scrollContainerRef.current.scrollBy({ left: 300, behavior: 'smooth' });
    }
  };
  
  return (
    <motion.div 
      className={`flex ${isUser ? "justify-end" : "justify-start"} mb-6`}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {!isUser && (
        <div className="h-10 w-10 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center mr-3 flex-shrink-0 shadow-md">
          <Bot size={20} className="text-white" />
        </div>
      )}
      
      <div className={`max-w-[85%] ${isUser ? "order-1" : "order-2"} relative group`}>
        <div
          className={`px-5 py-3.5 rounded-2xl shadow-soft ${
            isUser 
              ? "bg-gradient-to-r from-blue-500 to-indigo-600 text-white" 
              : "bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 text-gray-800 dark:text-gray-200"
          }`}
        >
          {isUser ? (
            <p className="text-sm leading-relaxed">{message.content}</p>
          ) : (
            <div className="prose prose-sm dark:prose-invert max-w-none">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {message.content}
              </ReactMarkdown>
            </div>
          )}
        </div>

        {/* Copy button for assistant messages */}
        {!isUser && (
          <button 
            onClick={handleCopy}
            className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity p-1.5 rounded-full bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 z-10"
          >
            {copied ? (
              <Check size={14} className="text-green-500" />
            ) : (
              <Copy size={14} className="text-gray-500 dark:text-gray-400" />
            )}
          </button>
        )}

        {/* Product cards for assistant messages - Horizontal Scroll */}
        {!isUser && message.products && message.products.length > 0 && (
          <div className="mt-4 space-y-4">
            <div className="flex items-center justify-between bg-gray-50 dark:bg-gray-700/50 rounded-lg p-2.5">
              <div className="flex items-center gap-2">
                <span className="h-6 w-6 flex items-center justify-center rounded-full bg-blue-100 dark:bg-blue-900/30">
                  <span className="text-xs font-medium text-blue-600 dark:text-blue-400">{message.products.length}</span>
                </span>
                <p className="text-sm text-gray-700 dark:text-gray-300">
                  พบอุปกรณ์ IT ที่เกี่ยวข้อง
                </p>
              </div>
              {message.products.length > 6 && (
                <button 
                  onClick={() => setShowAllProducts(!showAllProducts)}
                  className="text-xs text-blue-600 dark:text-blue-400 flex items-center hover:underline"
                >
                  {showAllProducts ? "แสดงน้อยลง" : "แสดงทั้งหมด"}
                  <ChevronDown 
                    size={14} 
                    className={`ml-1 transition-transform ${showAllProducts ? "rotate-180" : ""}`} 
                  />
                </button>
              )}
            </div>
            
            <div className="relative">
              {/* Scroll buttons */}
              <button 
                onClick={scrollLeft} 
                className="absolute left-0 top-1/2 -translate-y-1/2 z-10 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm p-2 rounded-full shadow-md border border-gray-200 dark:border-gray-700"
                aria-label="Scroll left"
              >
                <ChevronLeft size={20} className="text-gray-600 dark:text-gray-400" />
              </button>
              
              <div 
                ref={scrollContainerRef}
                className="flex overflow-x-auto gap-4 py-2 px-8 snap-x snap-mandatory no-scrollbar"
              >
                {productsToShow?.map((product) => (
                  <motion.div
                    key={product._id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3 }}
                    className="snap-center flex-shrink-0 w-64"
                  >
                    <ProductCard product={product} />
                  </motion.div>
                ))}
              </div>
              
              <button 
                onClick={scrollRight} 
                className="absolute right-0 top-1/2 -translate-y-1/2 z-10 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm p-2 rounded-full shadow-md border border-gray-200 dark:border-gray-700"
                aria-label="Scroll right"
              >
                <ChevronRight size={20} className="text-gray-600 dark:text-gray-400" />
              </button>
            </div>
            
            {message.products.length > 6 && !showAllProducts && (
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => setShowAllProducts(true)}
                className="w-full py-2.5 bg-blue-50 dark:bg-blue-900/20 hover:bg-blue-100 dark:hover:bg-blue-800/30 rounded-lg text-sm text-blue-600 dark:text-blue-400 transition-colors flex items-center justify-center border border-blue-100 dark:border-blue-900/30"
              >
                แสดงสินค้าเพิ่มเติม ({message.products.length - 6} รายการ)
                <ChevronDown size={16} className="ml-1" />
              </motion.button>
            )}
          </div>
        )}

        <div className={`flex items-center gap-1.5 mt-1.5 ${isUser ? "justify-end" : "justify-start"}`}>
          <Clock size={12} className="text-gray-400 dark:text-gray-500" />
          <span className="text-xs text-gray-500 dark:text-gray-400">
            {formatTime(message.timestamp)}
          </span>
        </div>
      </div>

      {isUser && (
        <div className="h-10 w-10 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center ml-3 flex-shrink-0 shadow-md">
          <User size={18} className="text-white" />
        </div>
      )}
    </motion.div>
  )
}
