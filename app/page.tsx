"use client"

import { useState, useRef, useEffect } from "react"
import { ChatBubble } from "@/components/ChatBubble"
import { ChatInput } from "@/components/ChatInput"
import { ThemeToggle } from "@/components/theme-toggle"
import type { ChatMessage } from "@/types"
import { MessageCircle, ShoppingBag, Search, Menu, Bell, User as UserIcon, ChevronRight, Sparkles, X, ArrowUp, ArrowDown } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"

// Suggested questions for the user
const suggestions = ["สินค้าแนะนำ", "หมวดหมู่เครื่องประดับ", "เสื้อผ้าแนะนำ", "เสื้อผ้าราคาถูกแต่ดี"];

// Categories for quick navigation
const categories = [
  { name: "อิเล็กทรอนิกส์", icon: "💻" },
  { name: "แฟชั่น", icon: "👕" },
  { name: "ความงาม", icon: "✨" },
  { name: "บ้านและสวน", icon: "🏡" },
  { name: "กีฬา", icon: "⚽" },
  { name: "ของเล่น", icon: "🎮" },
];

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "1",
      role: "assistant",
      content:
        "สวัสดี! ฉันเป็นผู้ช่วยช้อปปิ้งอัจฉริยะของคุณ พร้อมช่วยคุณค้นหาสินค้าที่ต้องการ คุณสามารถถามฉันเกี่ยวกับสินค้าเฉพาะ หมวดหมู่ หรือตามงบประมาณของคุณได้!",
      timestamp: new Date(),
    },
  ])
  const [isLoading, setIsLoading] = useState(false)
  const [searchTerm, setSearchTerm] = useState("")
  const [showScrollTop, setShowScrollTop] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const chatContainerRef = useRef<HTMLDivElement>(null)
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const [shouldScrollToBottom, setShouldScrollToBottom] = useState(false)
  const [hasNewMessage, setHasNewMessage] = useState(false)
  const [isAtBottom, setIsAtBottom] = useState(true)

  const scrollToBottom = () => {
    if (shouldScrollToBottom) {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
      setShouldScrollToBottom(false)
    }
    setHasNewMessage(false)
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    // Check if we have new messages but user hasn't scrolled to bottom
    if (messages.length > 1 && !shouldScrollToBottom && !isAtBottom) {
      setHasNewMessage(true)
    }
  }, [messages, shouldScrollToBottom, isAtBottom])

  useEffect(() => {
    const handleScroll = () => {
      if (chatContainerRef.current) {
        const { scrollTop, scrollHeight, clientHeight } = chatContainerRef.current
        setShowScrollTop(scrollTop > 300)
        
        // Check if scrolled to bottom (with a small threshold)
        const isScrolledToBottom = scrollHeight - scrollTop - clientHeight < 50
        setIsAtBottom(isScrolledToBottom)
        
        if (isScrolledToBottom) {
          setHasNewMessage(false)
        }
      }
    }

    const chatContainer = chatContainerRef.current
    if (chatContainer) {
      chatContainer.addEventListener('scroll', handleScroll)
      return () => chatContainer.removeEventListener('scroll', handleScroll)
    }
  }, [])

  const handleSendMessage = async (content: string) => {
    // Set flag to scroll to bottom when user sends a message
    setShouldScrollToBottom(true)
    
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: "user",
      content,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setIsLoading(true)

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: content }),
      })

      if (!response.ok) {
        throw new Error("Failed to get response")
      }

      const data = await response.json()

      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: data.message,
        products: data.products || [],
        timestamp: new Date(),
      }

      setMessages((prev) => [...prev, assistantMessage])
    } catch (error) {
      console.error("Error:", error)
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "ขออภัย เกิดข้อผิดพลาดในการเชื่อมต่อ กรุณาลองอีกครั้ง!",
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  // Handle suggestion click
  const handleSuggestionClick = (suggestion: string) => {
    // Set flag to scroll to bottom when user clicks a suggestion
    setShouldScrollToBottom(true)
    handleSendMessage(suggestion);
  };
  
  // Handle search submission
  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchTerm.trim()) {
      // Set flag to scroll to bottom when user submits a search
      setShouldScrollToBottom(true)
      handleSendMessage(`ค้นหาสินค้า: ${searchTerm}`);
      setSearchTerm("");
    }
  };

  const scrollToTop = () => {
    chatContainerRef.current?.scrollTo({
      top: 0,
      behavior: 'smooth'
    })
  }

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-gray-900 dark:to-gray-800">
      {/* Header */}
      <header className="glass sticky top-0 z-50 border-b border-gray-200 dark:border-gray-700 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo and Title */}
            <div className="flex items-center gap-3">
              <div className="bg-gradient-to-r from-blue-600 to-indigo-600 p-2 rounded-xl shadow-md">
                <ShoppingBag className="text-white" size={24} />
              </div>
              <div>
                <h1 className="text-xl font-bold gradient-text">ShopSmart</h1>
                <p className="text-xs text-gray-500 dark:text-gray-400">AI-Powered Shopping Assistant</p>
              </div>
            </div>
            
            {/* Search */}
            <div className="hidden md:block flex-1 max-w-md mx-8">
              <form onSubmit={handleSearchSubmit}>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Search className="h-4 w-4 text-gray-400" />
                  </div>
                  <input
                    type="text"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="block w-full pl-10 pr-10 py-2 border border-gray-200 dark:border-gray-600 rounded-full bg-white/70 dark:bg-gray-800/70 backdrop-blur-sm text-sm text-gray-800 dark:text-gray-200 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all shadow-sm"
                    placeholder="ค้นหาสินค้า..."
                  />
                  {searchTerm && (
                    <button
                      type="button"
                      onClick={() => setSearchTerm("")}
                      className="absolute inset-y-0 right-0 pr-3 flex items-center"
                    >
                      <span className="text-gray-400 hover:text-gray-500 dark:hover:text-gray-300">
                        <X size={16} />
                      </span>
                    </button>
                  )}
                </div>
              </form>
            </div>
            
            {/* Right side icons */}
            <div className="flex items-center gap-3">
              <ThemeToggle />
              <button className="p-1.5 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-all">
                <Bell size={20} />
              </button>
              <button className="p-1.5 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-all">
                <UserIcon size={20} />
              </button>
              <button 
                className="md:hidden p-1.5 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-all"
                onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              >
                <Menu size={20} />
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Mobile menu */}
      <AnimatePresence>
        {isMobileMenuOpen && (
          <motion.div 
            className="md:hidden fixed inset-0 z-40 bg-gray-900/50 backdrop-blur-sm"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setIsMobileMenuOpen(false)}
          >
            <motion.div 
              className="absolute right-0 top-0 h-full w-64 bg-white dark:bg-gray-800 shadow-xl"
              initial={{ x: "100%" }}
              animate={{ x: 0 }}
              exit={{ x: "100%" }}
              transition={{ type: "spring", damping: 25, stiffness: 300 }}
              onClick={(e) => e.stopPropagation()}
            >
              <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
                <h2 className="font-semibold">เมนู</h2>
                <button 
                  className="p-1.5 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  <X size={18} />
                </button>
              </div>
              
              <div className="p-4">
                <form onSubmit={handleSearchSubmit} className="mb-6">
                  <div className="relative">
                    <input
                      type="text"
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="block w-full pl-3 pr-10 py-2 border border-gray-200 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 text-sm placeholder-gray-500 dark:placeholder-gray-400 dark:text-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="ค้นหาสินค้า..."
                    />
                    <button
                      type="submit"
                      className="absolute inset-y-0 right-0 pr-3 flex items-center"
                    >
                      <Search className="h-4 w-4 text-gray-400" />
                    </button>
                  </div>
                </form>
                
                <div className="space-y-4">
                  <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">หมวดหมู่สินค้า</h3>
                  <div className="space-y-2">
                    {categories.map((category, index) => (
                      <button
                        key={index}
                        className="flex items-center w-full p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-left"
                        onClick={() => {
                          handleSendMessage(`หมวดหมู่ ${category.name}`);
                          setIsMobileMenuOpen(false);
                        }}
                      >
                        <span className="mr-3 text-xl">{category.icon}</span>
                        <span>{category.name}</span>
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Categories bar (desktop only) */}
      <div className="hidden md:block bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-12 overflow-x-auto no-scrollbar">
            {categories.map((category, index) => (
              <button
                key={index}
                className="flex items-center px-3 py-1 text-sm text-gray-600 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 whitespace-nowrap transition-colors"
                onClick={() => handleSendMessage(`หมวดหมู่ ${category.name}`)}
              >
                <span className="mr-2">{category.icon}</span>
                {category.name}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Chat Messages */}
      <div 
        ref={chatContainerRef}
        className="flex-1 overflow-y-auto p-4 md:p-6 space-y-4 bg-gradient-to-b from-blue-50 to-white dark:from-gray-900 dark:to-gray-800"
      >
        <div className="max-w-3xl mx-auto w-full">
          {/* Suggested questions - show only if there's just the welcome message */}
          {messages.length === 1 && (
            <motion.div 
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3, duration: 0.5 }}
              className="mb-6 bg-white dark:bg-gray-800 rounded-xl p-4 shadow-soft border border-gray-100 dark:border-gray-700"
            >
              <div className="flex items-center gap-2 mb-3">
                <Sparkles size={18} className="text-blue-500" />
                <p className="text-sm font-medium text-gray-800 dark:text-gray-200">เริ่มต้นด้วยคำถามแนะนำ</p>
              </div>
              <div className="flex flex-wrap gap-2">
                {suggestions.map((suggestion, index) => (
                  <motion.button
                    key={index}
                    whileHover={{ scale: 1.03 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => handleSuggestionClick(suggestion)}
                    className="flex items-center gap-2 px-3 py-2 bg-blue-50 dark:bg-gray-700 border border-blue-100 dark:border-gray-600 rounded-lg text-sm text-gray-800 dark:text-gray-200 hover:bg-blue-100 dark:hover:bg-gray-600 transition-colors"
                  >
                    {suggestion}
                    <ChevronRight size={16} className="text-blue-500" />
                  </motion.button>
                ))}
              </div>
            </motion.div>
          )}

          <AnimatePresence>
            {messages.map((message) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.3 }}
              >
                <ChatBubble message={message} />
              </motion.div>
            ))}
          </AnimatePresence>

          {isLoading && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex justify-start mb-4"
            >
              <div className="glass rounded-2xl px-4 py-3 flex items-center gap-2 shadow-sm">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                </div>
                <span className="text-gray-600 dark:text-gray-300 text-sm">AI กำลังคิด...</span>
              </div>
            </motion.div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Scroll to top button */}
      <AnimatePresence>
        {showScrollTop && (
          <motion.button
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            className="fixed bottom-20 right-4 p-3 rounded-full bg-white dark:bg-gray-800 shadow-md border border-gray-200 dark:border-gray-700 text-blue-600 dark:text-blue-400 z-10"
            onClick={scrollToTop}
          >
            <ArrowUp size={20} />
          </motion.button>
        )}
      </AnimatePresence>

      {/* New message notification button */}
      <AnimatePresence>
        {hasNewMessage && !isAtBottom && (
          <motion.button
            initial={{ opacity: 0, scale: 0.8, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.8, y: 20 }}
            className="fixed bottom-20 left-1/2 transform -translate-x-1/2 py-2 px-4 rounded-full bg-blue-600 text-white shadow-md flex items-center gap-2 z-10"
            onClick={scrollToBottom}
          >
            <span>ข้อความใหม่</span>
            <ArrowDown size={16} />
          </motion.button>
        )}
      </AnimatePresence>

      {/* Chat Input */}
      <ChatInput onSendMessage={handleSendMessage} isLoading={isLoading} />
    </div>
  )
}
