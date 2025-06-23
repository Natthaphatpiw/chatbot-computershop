import { MongoClient, Db } from "mongodb"

if (!process.env.MONGODB_URI) {
  throw new Error("Please add your MongoDB URI to .env.local")
}

const uri = process.env.MONGODB_URI
const options = {
  serverSelectionTimeoutMS: 5000, // Timeout after 5s instead of 30s
  connectTimeoutMS: 10000,
  maxPoolSize: 10, // Maintain up to 10 socket connections
  retryWrites: true,
}

let client: MongoClient
let clientPromise: Promise<MongoClient>

if (process.env.NODE_ENV === "development") {
  const globalWithMongo = global as typeof globalThis & {
    _mongoClientPromise?: Promise<MongoClient>
  }

  if (!globalWithMongo._mongoClientPromise) {
    client = new MongoClient(uri, options)
    globalWithMongo._mongoClientPromise = client.connect()
  }
  clientPromise = globalWithMongo._mongoClientPromise
} else {
  client = new MongoClient(uri, options)
  clientPromise = client.connect()
}

// ✅ ฟังก์ชันนี้ใช้เพื่อเข้าถึง DB ได้สะดวก
export async function getDb(): Promise<Db> {
  const client = await clientPromise
  return client.db("dashboard-ai-data") // Updated to new database name
}

export default clientPromise
