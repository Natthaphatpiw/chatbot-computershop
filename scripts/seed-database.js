// Sample script to seed the MongoDB database with IT equipment data
// Run this script to populate your database with sample products

const { MongoClient } = require("mongodb")

const sampleProducts = [
  {
    "_id": "P101",
    "name": "โน้ตบุ๊ค MSI Modern 14",
    "description": "โน้ตบุ๊คขนาดกะทัดรัด Intel Core i7, SSD 512GB, RAM 16GB เหมาะสำหรับทำงานและพกพา",
    "price": 23900,
    "stock": 10,
    "category": "โน้ตบุ๊ค",
    "image_url": "https://via.placeholder.com/300x200?text=MSI+Modern+14",
    "tags": ["โน้ตบุ๊ค", "MSI", "Intel", "Portable"],
    "rating": 4.6,
    "reviews": 31
  },
  {
    "_id": "P102",
    "name": "คอมพิวเตอร์ตั้งโต๊ะ Gaming PC RTX 4060",
    "description": "คอมพิวเตอร์ประกอบสำหรับเล่นเกม Intel Core i9, RTX 4060, RAM 32GB, SSD 1TB",
    "price": 45900,
    "stock": 5,
    "category": "คอมพิวเตอร์ตั้งโต๊ะ",
    "image_url": "https://via.placeholder.com/300x200?text=Gaming+PC",
    "tags": ["Gaming", "RTX", "Intel", "Desktop"],
    "rating": 4.8,
    "reviews": 24
  },
  {
    "_id": "P103",
    "name": "เมาส์เกมมิ่ง Logitech G Pro X Superlight",
    "description": "เมาส์ไร้สายน้ำหนักเบาพิเศษ 63 กรัม เซนเซอร์ 25,600 DPI สำหรับเกมเมอร์",
    "price": 4590,
    "stock": 20,
    "category": "เกมมิ่งเกียร์",
    "image_url": "https://via.placeholder.com/300x200?text=Logitech+Mouse",
    "tags": ["Gaming", "Mouse", "Wireless", "Logitech"],
    "rating": 4.9,
    "reviews": 56
  },
  {
    "_id": "P104",
    "name": "SSD Samsung 980 Pro 1TB",
    "description": "SSD NVMe PCIe 4.0 ความเร็วสูง อ่าน 7,000MB/s เขียน 5,000MB/s",
    "price": 5290,
    "stock": 15,
    "category": "จัดเก็บข้อมูล",
    "image_url": "https://via.placeholder.com/300x200?text=Samsung+SSD",
    "tags": ["SSD", "Storage", "Samsung", "NVMe"],
    "rating": 4.7,
    "reviews": 42
  },
  {
    "_id": "P105",
    "name": "จอมอนิเตอร์ ASUS TUF Gaming 27 นิ้ว",
    "description": "จอมอนิเตอร์เกมมิ่ง 27 นิ้ว 165Hz 1ms IPS HDR FreeSync Premium",
    "price": 9990,
    "stock": 8,
    "category": "อุปกรณ์เสริม",
    "image_url": "https://via.placeholder.com/300x200?text=ASUS+Monitor",
    "tags": ["Monitor", "Gaming", "ASUS", "165Hz"],
    "rating": 4.5,
    "reviews": 38
  },
  {
    "_id": "P106",
    "name": "คีย์บอร์ด Mechanical Keychron K2",
    "description": "คีย์บอร์ด Mechanical แบบ 75% เชื่อมต่อได้ทั้ง Bluetooth และ USB-C",
    "price": 3290,
    "stock": 12,
    "category": "เกมมิ่งเกียร์",
    "image_url": "https://via.placeholder.com/300x200?text=Keychron+K2",
    "tags": ["Keyboard", "Mechanical", "Keychron", "Bluetooth"],
    "rating": 4.6,
    "reviews": 29
  },
  {
    "_id": "P107",
    "name": "โน้ตบุ๊ค ASUS ROG Zephyrus G14",
    "description": "โน้ตบุ๊คเกมมิ่งพกพา AMD Ryzen 9, RTX 3060, RAM 16GB, SSD 1TB, จอ 14 นิ้ว 144Hz",
    "price": 49900,
    "stock": 3,
    "category": "โน้ตบุ๊ค",
    "image_url": "https://via.placeholder.com/300x200?text=ASUS+ROG",
    "tags": ["Gaming", "ASUS", "ROG", "AMD", "Laptop"],
    "rating": 4.9,
    "reviews": 18
  },
  {
    "_id": "P108",
    "name": "External HDD WD Elements 4TB",
    "description": "ฮาร์ดดิสก์พกพาความจุ 4TB เชื่อมต่อผ่าน USB 3.0",
    "price": 3490,
    "stock": 25,
    "category": "จัดเก็บข้อมูล",
    "image_url": "https://via.placeholder.com/300x200?text=WD+HDD",
    "tags": ["HDD", "Storage", "External", "WD"],
    "rating": 4.3,
    "reviews": 47
  }
]

async function seedDatabase() {
  try {
    if (!process.env.MONGODB_URI) {
      throw new Error("MONGODB_URI is not defined in .env.local")
    }

    const client = new MongoClient(process.env.MONGODB_URI)
    await client.connect()
    console.log("Connected to MongoDB")

    const db = client.db("shopdb")
    const collection = db.collection("computershop")

    // Clear existing products
    await collection.deleteMany({})
    console.log("Cleared existing products")

    // Insert sample products
    const result = await collection.insertMany(sampleProducts)
    console.log(`Inserted ${result.insertedCount} products`)

    await client.close()
    console.log("Database seeded successfully!")
  } catch (error) {
    console.error("Error seeding database:", error)
    process.exit(1)
  }
}

seedDatabase()
