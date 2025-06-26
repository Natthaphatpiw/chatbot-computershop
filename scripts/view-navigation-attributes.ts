import { MongoClient } from "mongodb";
import dotenv from "dotenv";
import fs from "fs/promises";
import path from "path";

dotenv.config({ path: ".env.local" });

async function viewNavigationAttributes() {
  if (!process.env.MONGODB_URI) {
    throw new Error("Please add your MongoDB URI to .env.local");
  }

  const client = new MongoClient(process.env.MONGODB_URI);
  const outputFilePath = path.join(process.cwd(), "navigation_attributes.json");

  try {
    await client.connect();
    console.log("Connected to MongoDB");

    const db = client.db("dashboard-ai-data");
    const collection = db.collection("products");

    console.log("\nFetching distinct navigation attributes...");

    const [categoryMessage1Values] = await Promise.all([
      collection.distinct("cateName")
      // collection.distinct("navigation.categoryMessage2"),
      // collection.distinct("navigation.categoryMessage3"),
    ]);

    const navigationAttributes = {
      categoryMessage1: categoryMessage1Values,
      // categoryMessage2: categoryMessage2Values,
      // categoryMessage3: categoryMessage3Values,
    };

    await fs.writeFile(outputFilePath, JSON.stringify(navigationAttributes, null, 2));
    
    console.log(`\nSuccessfully saved navigation attributes to ${outputFilePath}`);

  } catch (error) {
    console.error("Error fetching or saving navigation attributes:", error);
  } finally {
    await client.close();
    console.log("\nConnection to MongoDB closed.");
  }
}

viewNavigationAttributes(); 