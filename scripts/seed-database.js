// Sample script to seed the MongoDB database with product data
// Run this script to populate your database with sample products

const { MongoClient } = require("mongodb")

const sampleProducts = [
  {
    name: "MacBook Pro 14-inch",
    description: "Apple MacBook Pro with M2 chip, 14-inch Liquid Retina XDR display, 16GB RAM, 512GB SSD",
    price: 1999.99,
    image: "/placeholder.svg?height=200&width=300",
    category: "electronics",
    inStock: true,
    rating: 4.8,
  },
  {
    name: "Nike Air Max 270",
    description: "Men's running shoes with Air Max cushioning and breathable mesh upper",
    price: 129.99,
    image: "/placeholder.svg?height=200&width=300",
    category: "sports",
    inStock: true,
    rating: 4.5,
  },
  {
    name: "The Great Gatsby",
    description: "Classic American novel by F. Scott Fitzgerald, paperback edition",
    price: 12.99,
    image: "/placeholder.svg?height=200&width=300",
    category: "books",
    inStock: true,
    rating: 4.2,
  },
  {
    name: 'Samsung 55" 4K Smart TV',
    description: "55-inch 4K UHD Smart TV with HDR and built-in streaming apps",
    price: 599.99,
    image: "/placeholder.svg?height=200&width=300",
    category: "electronics",
    inStock: false,
    rating: 4.6,
  },
  {
    name: "Levi's 501 Original Jeans",
    description: "Classic straight-leg jeans in dark wash, 100% cotton denim",
    price: 79.99,
    image: "/placeholder.svg?height=200&width=300",
    category: "clothing",
    inStock: true,
    rating: 4.3,
  },
  {
    name: "KitchenAid Stand Mixer",
    description: "5-quart tilt-head stand mixer with 10 speeds and multiple attachments",
    price: 299.99,
    image: "/placeholder.svg?height=200&width=300",
    category: "home",
    inStock: true,
    rating: 4.9,
  },
  {
    name: "Wireless Bluetooth Headphones",
    description: "Over-ear headphones with active noise cancellation and 30-hour battery",
    price: 199.99,
    image: "/placeholder.svg?height=200&width=300",
    category: "electronics",
    inStock: true,
    rating: 4.4,
  },
  {
    name: "Yoga Mat Premium",
    description: "Non-slip yoga mat with extra cushioning, 6mm thick, eco-friendly material",
    price: 49.99,
    image: "/placeholder.svg?height=200&width=300",
    category: "sports",
    inStock: true,
    rating: 4.7,
  },
]

async function seedDatabase() {
  const client = new MongoClient(process.env.MONGODB_URI)

  try {
    await client.connect()
    console.log("Connected to MongoDB")

    const db = client.db("store")
    const collection = db.collection("products")

    // Clear existing products
    await collection.deleteMany({})
    console.log("Cleared existing products")

    // Insert sample products
    const result = await collection.insertMany(sampleProducts)
    console.log(`Inserted ${result.insertedCount} products`)

    console.log("Database seeded successfully!")
  } catch (error) {
    console.error("Error seeding database:", error)
  } finally {
    await client.close()
  }
}

seedDatabase()
