"use client"

import { useState, Fragment } from "react"
import { Dialog, Transition } from "@headlessui/react"
import Image from "next/image"
import { X, Star, ShoppingCart, Heart, Share2 } from "lucide-react"
import type { Product } from "@/types"
import { motion } from "framer-motion"

interface ProductModalProps {
  product: Product
  isOpen: boolean
  onClose: () => void
}

export function ProductModal({ product, isOpen, onClose }: ProductModalProps) {
  const [selectedTab, setSelectedTab] = useState("details")
  const rating = product.rating ?? 0
  
  return (
    <Transition show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={onClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black bg-opacity-25 backdrop-blur-sm" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4 text-center">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <Dialog.Panel className="w-full max-w-3xl transform overflow-hidden rounded-2xl bg-white dark:bg-gray-800 p-6 text-left align-middle shadow-xl transition-all">
                <div className="absolute top-4 right-4">
                  <button
                    type="button"
                    className="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 transition-colors"
                    onClick={onClose}
                  >
                    <X size={24} />
                  </button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Product Image */}
                  <div className="relative h-80 w-full rounded-lg overflow-hidden">
                    <Image
                      src={product.image_url || "/placeholder.svg?height=400&width=600"}
                      alt={product.name}
                      fill
                      className="object-cover"
                    />
                    {!product.inStock && (
                      <div className="absolute top-4 left-4 bg-red-500 text-white px-3 py-1 rounded-md text-sm font-medium">
                        Out of Stock
                      </div>
                    )}
                    {product.rating && product.rating >= 4.5 && (
                      <div className="absolute bottom-4 left-4 bg-yellow-400 text-yellow-900 px-3 py-1 rounded-md text-sm font-medium flex items-center gap-1">
                        <Star size={16} fill="currentColor" /> Top Rated
                      </div>
                    )}
                  </div>

                  {/* Product Details */}
                  <div>
                    <div className="flex items-center text-sm text-gray-500 dark:text-gray-400 mb-2">
                      <span className="capitalize bg-gray-100 dark:bg-gray-700 px-2 py-0.5 rounded-full">
                        {product.category}
                      </span>
                    </div>
                    <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">{product.name}</h2>
                    
                    <div className="flex items-center gap-2 mb-4">
                      <div className="flex">
                        {[...Array(5)].map((_, i) => (
                          <Star
                            key={i}
                            size={16}
                            className={i < Math.floor(rating) ? "text-yellow-400" : "text-gray-300 dark:text-gray-600"}
                            fill={i < Math.floor(rating) ? "currentColor" : "none"}
                          />
                        ))}
                      </div>
                      {product.rating && (
                        <span className="text-sm text-gray-600 dark:text-gray-300">
                          {product.rating} (24 รีวิว)
                        </span>
                      )}
                    </div>

                    <div className="text-3xl font-bold text-blue-600 dark:text-blue-400 mb-6">
                      ${product.price.toFixed(2)}
                    </div>

                    <div className="mb-6">
                      <div className="flex space-x-2 mb-4">
                        <button
                          className={`px-4 py-1 text-sm rounded-full transition-colors ${
                            selectedTab === "details"
                              ? "bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400"
                              : "bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300"
                          }`}
                          onClick={() => setSelectedTab("details")}
                        >
                          รายละเอียด
                        </button>
                        <button
                          className={`px-4 py-1 text-sm rounded-full transition-colors ${
                            selectedTab === "reviews"
                              ? "bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400"
                              : "bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300"
                          }`}
                          onClick={() => setSelectedTab("reviews")}
                        >
                          รีวิว
                        </button>
                      </div>

                      {selectedTab === "details" ? (
                        <p className="text-gray-600 dark:text-gray-300 text-sm">{product.description}</p>
                      ) : (
                        <div className="space-y-4">
                          <div className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                            <div className="flex items-center gap-2 mb-2">
                              <div className="h-8 w-8 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center">
                                <span className="text-sm font-medium text-blue-600 dark:text-blue-400">JD</span>
                              </div>
                              <div>
                                <p className="text-sm font-medium text-gray-900 dark:text-gray-100">John Doe</p>
                                <div className="flex items-center">
                                  {[...Array(5)].map((_, i) => (
                                    <Star
                                      key={i}
                                      size={12}
                                      className={i < 5 ? "text-yellow-400" : "text-gray-300"}
                                      fill={i < 5 ? "currentColor" : "none"}
                                    />
                                  ))}
                                </div>
                              </div>
                            </div>
                            <p className="text-sm text-gray-600 dark:text-gray-300">
                              สินค้าคุณภาพดีมาก ส่งไว ใช้งานได้ดี คุ้มราคา แนะนำเลยครับ
                            </p>
                          </div>
                          <div className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                            <div className="flex items-center gap-2 mb-2">
                              <div className="h-8 w-8 rounded-full bg-green-100 dark:bg-green-900 flex items-center justify-center">
                                <span className="text-sm font-medium text-green-600 dark:text-green-400">AM</span>
                              </div>
                              <div>
                                <p className="text-sm font-medium text-gray-900 dark:text-gray-100">Alice Miller</p>
                                <div className="flex items-center">
                                  {[...Array(5)].map((_, i) => (
                                    <Star
                                      key={i}
                                      size={12}
                                      className={i < 4 ? "text-yellow-400" : "text-gray-300"}
                                      fill={i < 4 ? "currentColor" : "none"}
                                    />
                                  ))}
                                </div>
                              </div>
                            </div>
                            <p className="text-sm text-gray-600 dark:text-gray-300">
                              ใช้งานดี แต่จัดส่งช้าไปนิด โดยรวมพอใจ
                            </p>
                          </div>
                        </div>
                      )}
                    </div>

                    <div className="flex gap-2">
                      <button
                        className={`flex-1 py-2.5 px-4 rounded-lg flex items-center justify-center gap-2 transition-colors ${
                          product.inStock
                            ? "bg-blue-600 hover:bg-blue-700 text-white"
                            : "bg-gray-100 dark:bg-gray-700 text-gray-400 dark:text-gray-500 cursor-not-allowed"
                        }`}
                        disabled={!product.inStock}
                      >
                        <ShoppingCart size={18} />
                        {product.inStock ? "Add to Cart" : "Out of Stock"}
                      </button>
                      <button className="p-2.5 rounded-lg border border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
                        <Heart size={18} />
                      </button>
                      <button className="p-2.5 rounded-lg border border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
                        <Share2 size={18} />
                      </button>
                    </div>
                  </div>
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  )
} 