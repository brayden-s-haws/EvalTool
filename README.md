# EvalSwipe - AI Trace Review Application

A lightweight web application designed to streamline the evaluation of AI system traces through systematic open and axial coding methodologies.

## Features

- **Swipe-based Review Interface**: Swipe through AI traces with intuitive gestures and keyboard shortcuts
- **Open & Axial Coding**: Systematic failure categorization using grounded theory methodology
- **Prompt Improvement**: AI-powered suggestions for improving system prompts based on failure patterns
- **Braintrust Integration**: Seamless import/export of traces and annotations
- **Session Management**: Save, resume, and export review sessions
- **Export Capabilities**: CSV, JSON, and PDF report generation

## Quick Start

### Prerequisites

- Python 3.10+
- Anthropic API key (for prompt improvement features)
- Braintrust API key (optional, for integration features)

### Installation

1. Clone the repository:
```bash
cd EvalTool
```

2. Create and activate virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r backend/requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

### Running the Application

1. Start the FastAPI backend:
```bash
cd backend
python app.py
```

2. Open your browser to `http://localhost:8000`

The application will be running with:
- Frontend UI at: `http://localhost:8000`
- API documentation at: `http://localhost:8000/api/docs`
- Health check at: `http://localhost:8000/health`

## Usage

### Creating a Session

1. Click "New Session" on the home page
2. Choose to:
   - Upload traces from JSON file
   - Import from Braintrust
   - Use demo snack recommendation data

### Reviewing Traces

- **Swipe Right** or press **P** or **→**: Mark as PASS
- **Swipe Left** or press **F** or **←**: Mark as FAIL (opens coding modal)
- **Swipe Up** or press **D** or **↑**: DEFER decision
- **Space**: Expand/collapse all trace details
- **Cmd/Ctrl + Z**: Undo last action

### Coding Workflow

1. **Open Coding**: Write freeform observations about failures
2. **Axial Coding**: Organize observations into structured categories (tags)
3. **Pattern Analysis**: View failure mode distribution and analytics

### Prompt Improvement

1. Navigate to "Prompt Improvement" tool
2. Paste your current system prompt
3. Select target failure modes to address
4. Review AI-generated improvement suggestions

## Project Structure

```
EvalTool/
├── backend/              # FastAPI application
│   ├── app.py           # Main application entry point
│   ├── models/          # Pydantic data models
│   ├── routes/          # API endpoints
│   ├── services/        # Business logic
│   └── requirements.txt # Python dependencies
├── frontend/            # Web interface
│   ├── index.html       # Main page
│   ├── css/            # Stylesheets
│   ├── js/             # JavaScript modules
│   └── assets/         # Static assets and demo data
├── tests/              # Test files
├── docs/               # Documentation
└── README.md
```

## API Documentation

Full API documentation is available at `/api/docs` when the server is running.

### Key Endpoints

- `GET /api/traces` - List all traces
- `POST /api/annotations` - Create trace annotation
- `GET /api/tags` - List all axial tags
- `POST /api/sessions` - Create new session
- `POST /api/prompt-improvement/suggest` - Generate prompt suggestions
- `POST /api/braintrust/import` - Import from Braintrust
- `GET /api/export/csv/{session_id}` - Export session as CSV

## Development

### Running Tests

```bash
pytest tests/
```

### Code Style

The project follows PEP 8 style guidelines for Python code.

## Configuration

Environment variables are configured in `.env` file:

- `ANTHROPIC_API_KEY`: Your Anthropic API key (required)
- `BRAINTRUST_API_KEY`: Your Braintrust API key (optional)
- `ENV`: Environment (development/production)
- `DEBUG`: Enable debug mode (true/false)
- `PORT`: Server port (default: 8000)

## Contributing

This is a research tool developed for AI evaluation workflows. Contributions and suggestions are welcome.

## License

[Add your license here]

## Acknowledgments

Built with:
- FastAPI
- Anthropic Claude API
- Braintrust
- Vanilla JavaScript

Methodology inspired by grounded theory and systematic coding practices from qualitative research.
