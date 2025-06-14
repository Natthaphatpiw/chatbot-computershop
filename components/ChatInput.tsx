"use client"

import type React from "react"

import { useState, useRef, useEffect } from "react"
import { Send, Mic, Smile, Paperclip, Loader2, Image, Camera } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"

interface ChatInputProps {
  onSendMessage: (message: string) => void
  isLoading: boolean
}

export function ChatInput({ onSendMessage, isLoading }: ChatInputProps) {
  const [input, setInput] = useState("")
  const [isFocused, setIsFocused] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)
  
  // Auto focus input on component mount
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus()
    }
  }, [])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (input.trim() && !isLoading) {
      onSendMessage(input.trim())
      setInput("")
    }
  }

  return (
    <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-md border-t border-gray-200 dark:border-gray-700 p-4 sticky bottom-0 z-30 shadow-md">
      <form onSubmit={handleSubmit} className="flex items-center gap-2 max-w-4xl mx-auto">
        <div className="flex-1 relative">
          <motion.div 
            className={`absolute inset-0 rounded-2xl transition-all duration-300 ${
              isFocused 
                ? "ring-2 ring-blue-500 shadow-md" 
                : "ring-1 ring-gray-200 dark:ring-gray-700"
            }`}
            animate={{ opacity: 1 }}
            initial={{ opacity: 0 }}
          />
          
          <div className="flex items-center relative bg-white dark:bg-gray-700 rounded-2xl px-4 py-1">
            <button
              type="button"
              disabled={isLoading}
              className={`p-2 rounded-full transition-colors ${
                isLoading 
                  ? "text-gray-400 dark:text-gray-600 cursor-not-allowed" 
                  : "text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600"
              }`}
            >
              <Paperclip size={18} />
            </button>
            
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onFocus={() => setIsFocused(true)}
              onBlur={() => setIsFocused(false)}
              placeholder={isLoading ? "กำลังประมวลผล..." : "ถามเกี่ยวกับสินค้า... (เช่น 'คีย์บอร์ดราคาถูก' หรือ 'หนังสือขายดี')"}
              className="w-full px-3 py-3 bg-transparent border-none focus:outline-none text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400"
              disabled={isLoading}
            />
            
            <div className="flex items-center gap-1">
              <button
                type="button"
                disabled={isLoading}
                className={`p-2 rounded-full transition-colors ${
                  isLoading
                    ? "text-gray-400 dark:text-gray-600 cursor-not-allowed"
                    : "text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600"
                }`}
              >
                <Image size={18} />
              </button>
              
              <button
                type="button"
                disabled={isLoading}
                className={`p-2 rounded-full transition-colors ${
                  isLoading
                    ? "text-gray-400 dark:text-gray-600 cursor-not-allowed"
                    : "text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600"
                }`}
              >
                <Camera size={18} />
              </button>
              
              <button
                type="button"
                disabled={isLoading}
                className={`p-2 rounded-full transition-colors ${
                  isLoading
                    ? "text-gray-400 dark:text-gray-600 cursor-not-allowed"
                    : "text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600"
                }`}
              >
                <Smile size={18} />
              </button>
            </div>
          </div>
        </div>
        
        <AnimatePresence mode="wait">
          {!input.trim() ? (
            <motion.button
              key="mic"
              type="button"
              disabled={isLoading}
              className={`p-3 rounded-full transition-all ${
                isLoading
                  ? "bg-gray-100 dark:bg-gray-700 text-gray-400 dark:text-gray-600 cursor-not-allowed"
                  : "bg-gradient-to-r from-blue-500 to-indigo-500 text-white hover:shadow-md active:scale-95"
              }`}
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
              transition={{ duration: 0.15 }}
            >
              <Mic size={20} />
            </motion.button>
          ) : (
            <motion.button
              key="send"
              type="submit"
              disabled={!input.trim() || isLoading}
              className={`p-3 rounded-full transition-all ${
                !input.trim() || isLoading
                  ? "bg-gray-400 dark:bg-gray-600 text-white cursor-not-allowed"
                  : "bg-gradient-to-r from-blue-500 to-indigo-500 text-white hover:shadow-md active:scale-95"
              }`}
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
              transition={{ duration: 0.15 }}
            >
              {isLoading ? (
                <Loader2 size={20} className="animate-spin" />
              ) : (
                <Send size={20} />
              )}
            </motion.button>
          )}
        </AnimatePresence>
      </form>
      
      {isLoading && (
        <div className="flex justify-center mt-2">
          <span className="text-xs text-gray-500 dark:text-gray-400 animate-pulse">
            กำลังประมวลผล...
          </span>
        </div>
      )}
    </div>
  )
}
