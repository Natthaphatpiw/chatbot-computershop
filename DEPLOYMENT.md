# Deployment Guide for Chatbot Computer Shop Backend

## Prerequisites

- Python 3.12+
- Docker and Docker Compose (for containerized deployment)
- MongoDB database
- OpenAI API key

## Environment Variables

Create a `.env` file in the backend directory:

```env
MONGODB_URL=mongodb://localhost:27017/chatbot_computershop
OPENAI_API_KEY=your_openai_api_key_here
ENVIRONMENT=production
```

## Option 1: Docker Deployment (Recommended)

### Build and Run with Docker Compose

```bash
# Build and start the service
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

### Manual Docker Build

```bash
# Build the image
docker build -t chatbot-backend .

# Run the container
docker run -d \
  --name chatbot-backend \
  -p 8000:8000 \
  --env-file .env \
  chatbot-backend
```

## Option 2: Direct Python Deployment

### Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run the Application

```bash
# Development mode
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Option 3: Production with Gunicorn

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Health Check

The application includes a health check endpoint:

```bash
curl http://localhost:8000/health
```

## API Documentation

Once deployed, access the API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Monitoring and Logs

### Docker Logs
```bash
docker-compose logs -f backend
```

### Application Logs
The application logs to stdout/stderr, which can be captured by your container runtime or process manager.

## Scaling

### Horizontal Scaling with Docker Compose
```yaml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "8000-8009:8000"
    deploy:
      replicas: 3
```

### Load Balancer Configuration
Use a reverse proxy like Nginx or Traefik to distribute traffic across multiple instances.

## Security Considerations

1. **Environment Variables**: Never commit API keys or sensitive data to version control
2. **Network Security**: Use HTTPS in production
3. **Database Security**: Ensure MongoDB is properly secured
4. **Container Security**: Run containers as non-root users
5. **Rate Limiting**: Implement rate limiting for API endpoints

## Troubleshooting

### Common Issues

1. **MongoDB Connection Error**
   - Verify MONGODB_URL is correct
   - Check if MongoDB is running and accessible

2. **OpenAI API Error**
   - Verify OPENAI_API_KEY is valid
   - Check API quota and billing

3. **Port Already in Use**
   - Change the port in docker-compose.yml or use a different port

4. **Permission Errors**
   - Ensure proper file permissions
   - Check Docker user permissions

### Debug Mode

For debugging, run with debug logging:

```bash
ENVIRONMENT=development uvicorn app.main:app --reload --log-level debug
``` 