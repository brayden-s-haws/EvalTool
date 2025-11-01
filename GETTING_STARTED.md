# Getting Started with EvalSwipe

Welcome! This guide will get you up and running with EvalSwipe in **under 5 minutes**.

## Quick Start

### 1. Activate Virtual Environment

```bash
source .venv/bin/activate
```

### 2. Start the Application

```bash
cd backend
python app.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Application startup complete.
```

### 3. Open in Browser

Navigate to: **http://localhost:8000**

### 4. Load Demo Data

1. Click **"Load Demo"** button on the welcome screen
2. You'll see 50 snack recommendation traces loaded
3. Start reviewing!

## First Review Session

### Basic Controls

- **Right Arrow (→)** or **P**: Mark trace as Pass
- **Left Arrow (←)** or **F**: Mark trace as Fail
- **Up Arrow (↑)** or **D**: Defer decision
- **Space**: Show/hide trace details

### Try This Workflow

1. **Review 5-10 traces** using pass/fail buttons
2. **Write open codes** for failures (what went wrong?)
3. **After 20 traces**, create axial tags to categorize failures
4. **View progress** in the tracker at the top

## Next Steps

### Add Your API Key (Optional for Demo)

For prompt improvement features, add your Anthropic API key:

1. Edit `.env` file in project root:
```bash
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

2. Restart the server

### Import Your Own Traces

Upload a JSON file with this format:

```json
{
  "traces": [
    {
      "id": "trace_001",
      "user_input": "User's question",
      "agent_output": "AI's response",
      "system_prompt": "Optional system prompt",
      "metadata": {}
    }
  ]
}
```

Click **"Upload JSON"** and select your file.

### Connect to Braintrust

1. Get your API credentials from Braintrust
2. Click **"Import from Braintrust"**
3. Enter: API Key, Project ID, Experiment ID
4. Click **"Fetch Traces"**

## Features to Explore

### Open Coding
- Write detailed observations about failures
- Use 50-500 characters for good notes
- Focus on what went wrong, not what should be

### Axial Coding
- Create tags like "Hallucinated Metadata", "Tone Mismatch"
- Group similar failures together
- Track frequency of each failure type

### Prompt Improvement
- Click **"Prompt Improvement"** in header
- Paste your current system prompt
- Select failure modes to address
- Get AI-generated improvement suggestions

### Export Options
- **CSV**: For spreadsheet analysis
- **JSON**: Complete data backup
- **PDF**: Summary report for stakeholders

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| → or P | Pass |
| ← or F | Fail |
| ↑ or D | Defer |
| Space | Toggle details |
| Cmd/Ctrl+Z | Undo |

## Troubleshooting

### Port 8000 Already in Use

Change port in `.env`:
```bash
PORT=8080
```

### Frontend Not Loading

Check the browser console (F12) for errors and verify files exist in `/frontend`.

### API Errors

Check server logs in the terminal where you ran `python app.py`.

## Learn More

- **[Setup Guide](docs/SETUP.md)**: Detailed installation instructions
- **[User Guide](docs/USER_GUIDE.md)**: Complete feature documentation
- **[API Documentation](docs/API.md)**: Integration details
- **[PRD](PRODUCT_REQUIREMENTS_DOCUMENT.md)**: Full specification

## Need Help?

1. Check server logs for errors
2. Review documentation in `/docs` folder
3. Verify API keys are set correctly in `.env`
4. Try demo data first to verify everything works

## What You've Built

EvalSwipe is a production-ready application with:

✅ **Full-stack architecture** (FastAPI backend + Vanilla JS frontend)
✅ **50 demo traces** for immediate testing
✅ **Open & axial coding** workflows
✅ **Claude API integration** for prompt improvements
✅ **Braintrust integration** for trace import/export
✅ **Export capabilities** (CSV, JSON, PDF)
✅ **Session management** with auto-save
✅ **Keyboard shortcuts** for 3-5x faster reviews
✅ **Comprehensive documentation**

## Ready to Go!

You're all set. Open http://localhost:8000 and start your first evaluation session!

Happy evaluating! 🚀
