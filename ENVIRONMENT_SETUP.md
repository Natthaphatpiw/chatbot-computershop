# Environment Setup Guide

## การตั้งค่า Environment Variables

### Local Development (ค่าเริ่มต้น)

สำหรับการพัฒนา local โดยไม่ต้องตั้งค่า environment variable ใดๆ:

```bash
# ไม่ต้องตั้งค่า NEXT_PUBLIC_API_URL
# ระบบจะใช้ค่าเริ่มต้น: http://localhost:8000
npm run dev
```

### Local Development (ใช้ Local Backend)

หากต้องการใช้ backend ที่รันใน local:

```bash
# แก้ไขไฟล์ .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Production (ใช้ Deployed Backend)

สำหรับ production หรือทดสอบกับ backend ที่ deploy แล้ว:

```bash
# แก้ไขไฟล์ .env.local
NEXT_PUBLIC_API_URL=https://chatbot-computershop-1.onrender.com
```

## ไฟล์ Environment Variables

### .env.local (สำหรับ Local Development)
```env
# Local Development - Backend URL
# Uncomment the line below to use local backend
# NEXT_PUBLIC_API_URL=http://localhost:8000

# Production - Uncomment to use deployed backend
# NEXT_PUBLIC_API_URL=https://chatbot-computershop-1.onrender.com
```

### .env.production (สำหรับ Production Build)
```env
NEXT_PUBLIC_API_URL=https://chatbot-computershop-1.onrender.com
```

## การทำงานของระบบ

1. **ค่าเริ่มต้น**: `http://localhost:8000` (สำหรับ local development)
2. **Override**: หากตั้งค่า `NEXT_PUBLIC_API_URL` ใน environment variables จะใช้ค่านั้นแทน
3. **API Routes**: Next.js API routes จะ proxy ไปยัง backend URL ที่กำหนด

## การทดสอบ

### ทดสอบ Local Backend
```bash
# 1. Start local backend
cd backend
python start.py

# 2. Start frontend (ในอีก terminal)
npm run dev

# 3. ทดสอบ API
curl -X POST http://localhost:3000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "สวัสดี"}'
```

### ทดสอบ Production Backend
```bash
# 1. Set environment variable
export NEXT_PUBLIC_API_URL=https://chatbot-computershop-1.onrender.com

# 2. Start frontend
npm run dev

# 3. ทดสอบ API
curl -X POST http://localhost:3000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "สวัสดี"}'
```

## หมายเหตุ

- Backend ที่ deploy แล้ว: [https://chatbot-computershop-1.onrender.com](https://chatbot-computershop-1.onrender.com)
- Local backend: `http://localhost:8000`
- Frontend: `http://localhost:3000` 