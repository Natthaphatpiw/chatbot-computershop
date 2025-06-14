"use client"

import * as React from "react"
import { Moon, Sun } from "lucide-react"
import { useTheme } from "next-themes"
import { motion } from "framer-motion"

export function ThemeToggle() {
  const { theme, setTheme } = useTheme()
  const [mounted, setMounted] = React.useState(false)

  React.useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return (
      <div className="w-9 h-9 flex items-center justify-center rounded-full border border-gray-200">
        <span className="sr-only">Toggle theme</span>
        <div className="w-5 h-5 bg-gray-200 rounded-full animate-pulse" />
      </div>
    )
  }

  return (
    <motion.button
      whileTap={{ scale: 0.9 }}
      onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
      className={`w-10 h-10 flex items-center justify-center rounded-full transition-colors ${
        theme === "dark" 
          ? "bg-gray-800 text-yellow-300 hover:bg-gray-700" 
          : "bg-blue-50 text-blue-600 hover:bg-blue-100"
      }`}
    >
      <span className="sr-only">Toggle theme</span>
      {theme === "dark" ? (
        <motion.div
          initial={{ rotate: -45 }}
          animate={{ rotate: 0 }}
          transition={{ duration: 0.3 }}
        >
          <Sun size={20} />
        </motion.div>
      ) : (
        <motion.div
          initial={{ rotate: 45 }}
          animate={{ rotate: 0 }}
          transition={{ duration: 0.3 }}
        >
          <Moon size={20} />
        </motion.div>
      )}
    </motion.button>
  )
}
