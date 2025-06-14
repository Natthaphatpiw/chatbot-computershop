"use client"

import type React from "react"

import { useState, useRef, useEffect } from "react"
import { Send, Mic, Smile, Paperclip, Loader2 } from "lucide-react"
import { motion } from "framer-motion"

interface ChatInputProps {
  onSendMessage: (message: string) => void
  isLoading: boolean
}

export function ChatInput({ onSendMessage, isLoading }: ChatInputProps) {
  const [input, setInput] = useState("")
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
    <div className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 p-4">
      <form onSubmit={handleSubmit} className="flex items-center gap-2 max-w-4xl mx-auto">
        <button
          type="button"
          disabled={isLoading}
          className={`p-2 rounded-full transition-colors ${
            isLoading 
              ? "text-gray-400 dark:text-gray-600 cursor-not-allowed" 
              : "text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
          }`}
        >
          <Paperclip size={20} />
        </button>
        
        <div className="relative flex-1">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={isLoading ? "กำลังประมวลผล..." : "ถามเกี่ยวกับสินค้า... (เช่น 'คีย์บอร์ดราคาถูก' หรือ 'หนังสือขายดี')"}
            className={`w-full px-4 py-3 pr-12 border rounded-full focus:outline-none focus:ring-2 shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 transition-colors ${
              isLoading 
                ? "border-gray-200 dark:border-gray-600 text-gray-400 dark:text-gray-500 cursor-not-allowed" 
                : "border-gray-300 dark:border-gray-600 focus:ring-blue-500 focus:border-transparent"
            }`}
            disabled={isLoading}
          />
          <button
            type="button"
            disabled={isLoading}
            className={`absolute right-12 top-1/2 -translate-y-1/2 transition-colors ${
              isLoading
                ? "text-gray-400 dark:text-gray-600 cursor-not-allowed"
                : "text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300"
            }`}
          >
            <Smile size={20} />
          </button>
        </div>
        
        {!input.trim() ? (
          <button
            type="button"
            disabled={isLoading}
            className={`p-3 rounded-full transition-colors ${
              isLoading
                ? "bg-gray-100 dark:bg-gray-700 text-gray-400 dark:text-gray-600 cursor-not-allowed"
                : "bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 hover:bg-blue-200 dark:hover:bg-blue-800/40"
            }`}
          >
            <Mic size={20} />
          </button>
        ) : (
          <motion.button
            type="submit"
            disabled={!input.trim() || isLoading}
            className={`p-3 rounded-full transition-colors ${
              !input.trim() || isLoading
                ? "bg-gray-400 dark:bg-gray-600 text-white cursor-not-allowed"
                : "bg-blue-600 hover:bg-blue-700 text-white"
            }`}
            whileTap={{ scale: 0.95 }}
          >
            {isLoading ? (
              <Loader2 size={20} className="animate-spin" />
            ) : (
              <Send size={20} />
            )}
          </motion.button>
        )}
      </form>
      
      {isLoading && (
        <div className="flex justify-center mt-2">
          <span className="text-xs text-gray-500 dark:text-gray-400">
            กำลังประมวลผล...
          </span>
        </div>
      )}
    </div>
  )
}
