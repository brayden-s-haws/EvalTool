# EvalSwipe Setup Guide

## Prerequisites

- Python 3.10 or higher
- pip (Python package installer)
- A modern web browser (Chrome, Firefox, Safari, or Edge)
- Anthropic API key (for prompt improvement features)
- Braintrust API key (optional, for Braintrust integration)

## Installation Steps

### 1. Navigate to Project Directory

```bash
cd /Users/haws/Documents/Projects/Code/PycharmProjects/EvalTool
```

### 2. Create Virtual Environment

If you haven't already created a virtual environment:

```bash
python3 -m venv .venv
```

### 3. Activate Virtual Environment

On macOS/Linux:
```bash
source .venv/bin/activate
```

On Windows:
```bash
.venv\Scripts\activate
```

### 4. Install Python Dependencies

```bash
pip install -r backend/requirements.txt
```

### 5. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` file and add your API keys:

```bash
# Required for prompt improvement
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Optional for Braintrust integration
BRAINTRUST_API_KEY=your-braintrust-key
BRAINTRUST_ORG_ID=your-org-id
BRAINTRUST_PROJECT_ID=your-project-id

# Server settings (optional)
HOST=0.0.0.0
PORT=8000
DEBUG=true
LOG_LEVEL=INFO
```

### 6. Start the Application

```bash
cd backend
python app.py
```

You should see output like:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 7. Access the Application

Open your web browser and navigate to:

```
http://localhost:8000
```

You should see the EvalSwipe welcome screen with options to:
- Load demo data
- Import from Braintrust
- Upload JSON traces

## Verifying Installation

### Check API Documentation

Navigate to `http://localhost:8000/api/docs` to view the interactive API documentation.

### Check Health Endpoint

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development"
}
```

### Test with Demo Data

1. Click "Load Demo" button on the welcome screen
2. You should see 50 snack recommendation traces loaded
3. Try reviewing a few traces with the swipe interface

## Troubleshooting

### Port Already in Use

If port 8000 is already in use, you can change it in `.env`:

```bash
PORT=8080
```

Then restart the server.

### Import Errors

If you get import errors, ensure you're in the correct directory and the virtual environment is activated:

```bash
cd backend
python -c "import fastapi; print('FastAPI OK')"
```

### API Key Issues

If prompt improvement isn't working, verify your Anthropic API key:

```bash
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01"
```

### Frontend Not Loading

If the frontend doesn't load:

1. Check browser console for errors (F12 or Right-click → Inspect)
2. Verify files exist in `/frontend` directory
3. Check CORS settings in `.env` if serving from different port

## Development Mode

For development with auto-reload:

```bash
cd backend
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

## Production Deployment

For production deployment:

1. Set `DEBUG=false` in `.env`
2. Use a production WSGI server (e.g., gunicorn)
3. Set up HTTPS
4. Configure proper CORS origins

```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app --bind 0.0.0.0:8000
```

## Next Steps

- Read the [User Guide](USER_GUIDE.md) for usage instructions
- Review the [API Documentation](API.md) for integration details
- Load your own traces and start reviewing!

## Getting Help

If you encounter issues:

1. Check the console output for error messages
2. Review the logs (set `LOG_LEVEL=DEBUG` in `.env`)
3. Consult the PRD for expected behavior
4. Create an issue with detailed error information
