# EvalSwipe API Documentation

## Base URL

```
http://localhost:8000/api
```

## Interactive Documentation

FastAPI provides automatic interactive documentation:

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

## Authentication

Currently, the API does not require authentication. For production deployments, implement authentication middleware.

## Endpoints

### Health Check

#### `GET /health`

Check if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development"
}
```

---

## Traces

### Get All Traces

#### `GET /api/traces`

Retrieve all traces with optional filtering.

**Query Parameters:**
- `reviewed` (boolean, optional): Filter by review status
- `pass_fail` (string, optional): Filter by judgment ("pass", "fail", "defer")

**Response:**
```json
{
  "traces": [
    {
      "id": "trace_001",
      "user_input": "string",
      "agent_output": "string",
      "reviewed": false,
      "pass_fail": null
    }
  ],
  "count": 100
}
```

### Get Single Trace

#### `GET /api/traces/{trace_id}`

Retrieve a specific trace by ID.

**Response:**
```json
{
  "id": "trace_001",
  "user_input": "string",
  "agent_output": "string",
  "system_prompt": "string",
  "intermediate_steps": [],
  "metadata": {},
  "reviewed": true,
  "pass_fail": "pass",
  "open_code": "string",
  "axial_tags": ["tag_001"],
  "reviewer_id": "user@example.com",
  "reviewed_at": "2025-01-15T10:30:00Z"
}
```

### Import Traces

#### `POST /api/traces/import`

Import multiple traces.

**Request Body:**
```json
{
  "traces": [
    {
      "id": "trace_001",
      "user_input": "string",
      "agent_output": "string"
    }
  ],
  "session_config": {
    "session_id": "optional_id"
  }
}
```

**Response:**
```json
{
  "success": true,
  "imported_count": 50,
  "session_id": "session_abc123"
}
```

---

## Annotations

### Create Annotation

#### `POST /api/annotations/`

Create or update annotation for a trace.

**Request Body:**
```json
{
  "trace_id": "trace_001",
  "pass_fail": "fail",
  "open_code": "Agent hallucinated metadata",
  "axial_tags": ["tag_001", "tag_002"],
  "reviewer_id": "user@example.com"
}
```

**Response:**
```json
{
  "success": true,
  "trace": { /* full trace object */ }
}
```

### Update Annotation

#### `PUT /api/annotations/{trace_id}`

Update existing annotation.

**Request Body:** Same as POST

**Response:**
```json
{
  "success": true,
  "trace": { /* full trace object */ }
}
```

### Delete Annotation

#### `DELETE /api/annotations/{trace_id}`

Remove annotation from trace.

**Response:**
```json
{
  "success": true,
  "message": "Annotation removed from trace trace_001"
}
```

---

## Tags

### Get All Tags

#### `GET /api/tags`

Retrieve all axial tags.

**Response:**
```json
{
  "tags": [
    {
      "id": "tag_001",
      "name": "Hallucinated Metadata",
      "description": "Agent invented facts not in source",
      "color": "#EF4444",
      "created_at": "2025-01-15T10:00:00Z",
      "usage_count": 12,
      "examples": ["Example 1", "Example 2"]
    }
  ]
}
```

### Create Tag

#### `POST /api/tags`

Create new axial tag.

**Request Body:**
```json
{
  "name": "Tone Mismatch",
  "description": "Response formality doesn't match user's style",
  "color": "#F59E0B"
}
```

**Response:**
```json
{
  "success": true,
  "tag": { /* full tag object */ }
}
```

### Update Tag

#### `PUT /api/tags/{tag_id}`

Update tag properties.

**Request Body:**
```json
{
  "name": "Updated Name",
  "description": "Updated description",
  "color": "#3B82F6"
}
```

**Response:**
```json
{
  "success": true,
  "tag": { /* full tag object */ }
}
```

### Delete Tag

#### `DELETE /api/tags/{tag_id}?untag_traces=true`

Delete tag and optionally untag all traces.

**Query Parameters:**
- `untag_traces` (boolean, default true): Remove tag from all traces

**Response:**
```json
{
  "success": true,
  "traces_affected": 15
}
```

### Merge Tags

#### `POST /api/tags/merge`

Merge two tags into one.

**Request Body:**
```json
{
  "source_tag_id": "tag_001",
  "target_tag_id": "tag_002"
}
```

**Response:**
```json
{
  "success": true,
  "merged_tag": { /* full tag object */ },
  "traces_affected": 10
}
```

---

## Sessions

### Get All Sessions

#### `GET /api/sessions`

List all saved sessions.

**Response:**
```json
{
  "sessions": [
    {
      "id": "session_abc123",
      "name": "Demo Session",
      "created_at": "2025-01-15T10:00:00Z",
      "total_traces": 50,
      "reviewed_count": 25,
      "source": "demo"
    }
  ]
}
```

### Get Session

#### `GET /api/sessions/{session_id}`

Load specific session.

**Response:**
```json
{
  "id": "session_abc123",
  "name": "Demo Session",
  "created_at": "2025-01-15T10:00:00Z",
  "traces": [ /* array of traces */ ],
  "axial_tags": [ /* array of tags */ ],
  "total_traces": 50,
  "reviewed_count": 25,
  "passed_count": 15,
  "failed_count": 8,
  "deferred_count": 2
}
```

### Create Session

#### `POST /api/sessions`

Create new session.

**Request Body:**
```json
{
  "name": "My Session",
  "traces": [ /* array of traces */ ],
  "config": {
    "mode": "combined",
    "randomize_order": false,
    "source": "upload"
  }
}
```

**Response:**
```json
{
  "success": true,
  "session": { /* full session object */ }
}
```

### Update Session

#### `PUT /api/sessions/{session_id}`

Update session (auto-save).

**Request Body:** Full session object

**Response:**
```json
{
  "success": true
}
```

### Delete Session

#### `DELETE /api/sessions/{session_id}`

Delete session.

**Response:**
```json
{
  "success": true
}
```

---

## Prompt Improvement

### Generate Suggestions

#### `POST /api/prompt-improvement/suggest`

Generate prompt improvement suggestions using Claude API.

**Request Body:**
```json
{
  "current_prompt": "You are a helpful assistant...",
  "target_failure_modes": ["tag_001", "tag_002"],
  "additional_context": "Focus on tone matching",
  "num_suggestions": 3
}
```

**Response:**
```json
{
  "suggestions": [
    {
      "version": 1,
      "improved_prompt": "Enhanced prompt text...",
      "changes_made": [
        "Added instruction for tone matching",
        "Included examples of good responses"
      ],
      "targeted_failures": ["Tone Mismatch", "Incomplete Response"]
    }
  ]
}
```

**Errors:**
- `500`: ANTHROPIC_API_KEY not configured
- `500`: Failed to generate suggestions (API error)

---

## Braintrust Integration

### Import from Braintrust

#### `POST /api/braintrust/import`

Import traces from Braintrust.

**Request Body:**
```json
{
  "api_key": "optional_if_in_env",
  "project_id": "proj_123",
  "experiment_id": "exp_456",
  "filters": {
    "limit": 100
  }
}
```

**Response:**
```json
{
  "success": true,
  "imported_count": 100,
  "traces": [ /* array of traces */ ],
  "cursor": "next_page_cursor"
}
```

**Errors:**
- `400`: API key not provided and not in environment
- `500`: Failed to fetch from Braintrust API

### Export to Braintrust

#### `POST /api/braintrust/export`

Export annotations to Braintrust.

**Request Body:**
```json
{
  "api_key": "optional_if_in_env",
  "project_id": "proj_123",
  "experiment_id": "exp_456",
  "trace_ids": ["trace_001", "trace_002"]
}
```

**Response:**
```json
{
  "success": true,
  "exported_count": 50,
  "failures": [
    {
      "trace_id": "trace_003",
      "error": "Trace not found"
    }
  ]
}
```

**Errors:**
- `400`: API key not provided and not in environment
- `500`: Failed to export to Braintrust API

---

## Export

### Export CSV

#### `GET /api/export/csv/{session_id}`

Export session as CSV file.

**Response:** CSV file download

### Export JSON

#### `GET /api/export/json/{session_id}`

Export session as JSON file.

**Response:** JSON file download

### Export PDF

#### `GET /api/export/pdf/{session_id}`

Generate PDF report.

**Response:** PDF file download

---

## Error Responses

All endpoints follow consistent error format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

**Common HTTP Status Codes:**
- `200`: Success
- `400`: Bad request (invalid input)
- `404`: Resource not found
- `500`: Internal server error

---

## Rate Limiting

Currently no rate limiting is implemented. For production, consider adding rate limiting middleware.

## CORS

CORS is configured in the backend. Allowed origins are set in `.env` via `ALLOWED_ORIGINS`.

Default: `http://localhost:3000,http://localhost:8080,http://127.0.0.1:3000`

## Data Persistence

Currently uses in-memory storage. All data is lost when server restarts. For production, integrate a database (PostgreSQL, MongoDB, etc.).

## Testing the API

### Using curl

```bash
# Health check
curl http://localhost:8000/health

# Get traces
curl http://localhost:8000/api/traces

# Create annotation
curl -X POST http://localhost:8000/api/annotations/ \
  -H "Content-Type: application/json" \
  -d '{
    "trace_id": "trace_001",
    "pass_fail": "pass",
    "reviewer_id": "test_user"
  }'
```

### Using Python

```python
import requests

# Get traces
response = requests.get('http://localhost:8000/api/traces')
traces = response.json()

# Create annotation
response = requests.post(
    'http://localhost:8000/api/annotations/',
    json={
        'trace_id': 'trace_001',
        'pass_fail': 'pass',
        'reviewer_id': 'test_user'
    }
)
```

### Using JavaScript

```javascript
// Get traces
const response = await fetch('http://localhost:8000/api/traces');
const data = await response.json();

// Create annotation
await fetch('http://localhost:8000/api/annotations/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        trace_id: 'trace_001',
        pass_fail: 'pass',
        reviewer_id: 'test_user'
    })
});
```

## Client Libraries

The application includes a JavaScript API client (`api-client.js`) for frontend integration.

For backend integrations, you can create similar clients in your language of choice using the endpoints documented above.
