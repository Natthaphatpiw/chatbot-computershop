# Chatbot Computer Shop Backend

Backend API สำหรับระบบ chatbot แนะนำสินค้าคอมพิวเตอร์ ใช้ FastAPI และ MongoDB

## Features

- **3-Stage AI Processing**: ระบบประมวลผล AI แบบ 3 ขั้นตอน
  - Stage 1: Phrase Segmentation และ Query Building
  - Stage 2: Content Analysis และ Product Matching
  - Stage 3: Question Answering และ Recommendations
- **MongoDB Integration**: เชื่อมต่อกับ MongoDB สำหรับจัดเก็บข้อมูลสินค้า
- **OpenAI Integration**: ใช้ OpenAI API สำหรับการประมวลผลภาษา
- **RESTful API**: API endpoints สำหรับ chat, recommendations, และ insights

## Quick Start

### Prerequisites

- Python 3.12+
- MongoDB
- OpenAI API key

### Installation

1. Clone the repository
2. Navigate to backend directory
3. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Copy environment file:
   ```bash
   cp env.example .env
   ```
6. Edit `.env` file with your configuration
7. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

## API Endpoints

### Chat Endpoint
```
POST /chat
```
สำหรับส่งข้อความและรับการตอบกลับจาก chatbot

### Recommendations Endpoint
```
POST /recommendations
```
สำหรับขอคำแนะนำสินค้า

### Trending Products
```
GET /trending
```
สำหรับดูสินค้าที่เป็นที่นิยม

### Insights
```
POST /insights
```
สำหรับวิเคราะห์ข้อมูลและ insights

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| MONGODB_URL | MongoDB connection string | mongodb://localhost:27017/chatbot_computershop |
| OPENAI_API_KEY | OpenAI API key | - |
| ENVIRONMENT | Environment (development/production) | development |
| DEBUG | Debug mode | false |

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── database.py          # MongoDB connection
│   ├── models.py            # Pydantic models
│   ├── routers/             # API routes
│   │   ├── chat.py
│   │   ├── recommendations.py
│   │   ├── trending.py
│   │   └── insights.py
│   └── services/            # Business logic
│       ├── chatbot.py       # Main chatbot service
│       └── two_stage_llm.py # AI processing logic
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose configuration
└── DEPLOYMENT.md           # Deployment guide
```

## Development

### Running Tests
```bash
python -m pytest
```

### Code Formatting
```bash
black .
isort .
```

### Type Checking
```bash
mypy .
```

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License. 