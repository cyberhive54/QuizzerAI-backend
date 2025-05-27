# Quiz Generator API

A FastAPI-based backend service for generating quizzes using OpenRouter's API.

## Deployment Requirements

### Environment Variables

The following environment variables must be set in your Railway deployment:

- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase API key
- `OPENROUTER_API_KEY`: Your OpenRouter API key
- `DEFAULT_MODEL`: Default model to use (e.g., gpt-3.5-turbo)
- `FRONTEND_URL`: URL of your frontend application
- `ADMIN_PASSWORD`: Password for admin dashboard access

### Railway Configuration

The project includes:
- `Procfile`: Defines the web process
- `railway.toml`: Railway-specific configuration
- `requirements.txt`: Python dependencies

### Health Checks

The API includes two health check endpoints:
- `/health`: Basic health check
- `/health/detailed`: Detailed health check including database status

### Logging

Logs are written to both:
- Console output
- `app.log` file

## Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables (see above)

3. Run the development server:
```bash
uvicorn app:app --reload
```

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Admin Dashboard

Access the admin dashboard at `/admin` with the configured admin password. 