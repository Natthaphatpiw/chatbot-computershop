require('dotenv').config({ path: '.env' });
const { MongoClient } = require('mongodb');

async function testConnection() {
  console.log('Testing MongoDB connection...');
  console.log('Connection string:', process.env.MONGODB_URI ? 'Found' : 'Not found');
  
  if (!process.env.MONGODB_URI) {
    console.error('❌ MONGODB_URI not found in environment variables');
    return;
  }

  const client = new MongoClient(process.env.MONGODB_URI, {
    serverSelectionTimeoutMS: 5000, // Timeout after 5s instead of 30s
    connectTimeoutMS: 10000,
  });

  try {
    console.log('🔄 Connecting to MongoDB...');
    await client.connect();
    console.log('✅ Connected successfully!');

    // Test database access
    const db = client.db('dashboard-ai-data');
    console.log('🔄 Testing database access...');
    
    // List collections
    const collections = await db.listCollections().toArray();
    console.log('📁 Available collections:', collections.map(c => c.name));
    
    // Test product_details collection
    const collection = db.collection('product_details');
    const count = await collection.countDocuments();
    console.log(`📊 Total products in product_details: ${count}`);
    
    if (count > 0) {
      // Get a sample product
      const sampleProduct = await collection.findOne({});
      console.log('📋 Sample product structure:');
      console.log(JSON.stringify(sampleProduct, null, 2));
    }

  } catch (error) {
    console.error('❌ Connection failed:', error.message);
    
    if (error.message.includes('ECONNRESET')) {
      console.log('\n💡 Troubleshooting tips:');
      console.log('1. Check if the MongoDB servers are running');
      console.log('2. Verify network connectivity to the servers');
      console.log('3. Check if firewall is blocking the connection');
      console.log('4. Verify authentication credentials');
    }
  } finally {
    await client.close();
    console.log('🔌 Connection closed');
  }
}

testConnection().catch(console.error);