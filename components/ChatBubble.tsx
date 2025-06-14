import type { ChatMessage } from "@/types"
import { ProductCard } from "./ProductCard"
import { User, Bot, Copy, Check, ChevronDown } from "lucide-react"
import { motion } from "framer-motion"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import { useState } from "react"

interface ChatBubbleProps {
  message: ChatMessage
}

export function ChatBubble({ message }: ChatBubbleProps) {
  const isUser = message.role === "user"
  const [copied, setCopied] = useState(false)
  const [showAllProducts, setShowAllProducts] = useState(false)
  const productsToShow = showAllProducts ? message.products : message.products?.slice(0, 3)
  
  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  
  return (
    <motion.div 
      className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {!isUser && (
        <div className="h-8 w-8 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center mr-2 flex-shrink-0">
          <Bot size={18} className="text-blue-600 dark:text-blue-400" />
        </div>
      )}
      
      <div className={`max-w-[80%] ${isUser ? "order-1" : "order-2"} relative group`}>
        <div
          className={`px-4 py-3 rounded-2xl shadow-sm ${
            isUser 
              ? "bg-gradient-to-r from-blue-500 to-blue-600 text-white" 
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
            className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity p-1 rounded-full bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600"
          >
            {copied ? (
              <Check size={14} className="text-green-500" />
            ) : (
              <Copy size={14} className="text-gray-500 dark:text-gray-400" />
            )}
          </button>
        )}

        {/* Product cards for assistant messages */}
        {!isUser && message.products && message.products.length > 0 && (
          <div className="mt-4 grid grid-cols-1 gap-4">
            <div className="flex items-center justify-between">
              <p className="text-xs text-gray-500 dark:text-gray-400">
                พบสินค้า {message.products.length} รายการ
              </p>
              {message.products.length > 3 && (
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
            
            {productsToShow?.map((product) => (
              <motion.div
                key={product._id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
              >
                <ProductCard product={product} />
              </motion.div>
            ))}
            
            {message.products.length > 3 && !showAllProducts && (
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => setShowAllProducts(true)}
                className="w-full py-2 bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 rounded-lg text-sm text-gray-600 dark:text-gray-300 transition-colors flex items-center justify-center"
              >
                แสดงสินค้าเพิ่มเติม ({message.products.length - 3} รายการ)
                <ChevronDown size={16} className="ml-1" />
              </motion.button>
            )}
          </div>
        )}

        <div className={`text-xs text-gray-500 dark:text-gray-400 mt-1 ${isUser ? "text-right" : "text-left"}`}>
          {message.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
        </div>
      </div>

      {isUser && (
        <div className="h-8 w-8 rounded-full bg-blue-600 flex items-center justify-center ml-2 flex-shrink-0">
          <User size={16} className="text-white" />
        </div>
      )}
    </motion.div>
  )
}
