## MVP Generator

**MVP Generator** is a small demo-ready tool that turns a short product idea into a full **developer starter pack**:

- **PRD-lite**
- **Architecture outline + mermaid diagram**
- **ERD + mermaid diagram**
- **API spec**
- **Task plan**

You can use the HTTP API (FastAPI) or the simple Streamlit UI. The app can run fully offline in **MOCK** LLM mode.

---

## Features

- **FastAPI** backend with `/generate`, `/history`, `/export`, and `/health`
- **SQLite** persistence for generation history (via SQLAlchemy 2.x)
- **Streamlit** single-page UI for quick demos
- **Loguru** logging with request-id middleware and LLM-specific log file
- **LLM integration** via OpenAI SDK or deterministic mock mode
- **Export to ZIP** with multiple Markdown files (PRD, Architecture, ERD, API spec, Tasks, README)

---

## Setup

### 1. Clone and enter the project

```bash
git clone <your-repo-url> mvp_generator
cd mvp_generator
```

### 2. Environment variables

Copy the example env file and edit as needed:

```bash
cp .env.example .env
```

Available variables:

- `OPENAI_API_KEY` – optional; if set and `LLM_MODE=openai`, the app will use OpenAI
- `OPENAI_MODEL` – defaults to `gpt-4.1-mini`
- `LLM_MODE` – `"mock"` (default when no key) or `"openai"`

When `LLM_MODE="mock"` or there is no API key, the app returns a deterministic, valid bundle suitable for demos and tests.

---

## Installing & Running

The repo includes a helper script `run.sh` for Unix-like environments.

### 1. Using `run.sh`

```bash
chmod +x run.sh
./run.sh
```

The script will:

- create a virtual environment (if missing),
- install dependencies from `requirements.txt`,
- start the FastAPI app using `uvicorn app.main:app --reload`.

You will see in the console how to start Streamlit separately.

### 2. Manual steps (alternative)

```bash
python -m venv .venv
source .venv/bin/activate      # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

uvicorn app.main:app --reload
```

FastAPI will default to `http://127.0.0.1:8000`.

---

## Running the Streamlit UI

With the virtual environment activated and requirements installed:

```bash
streamlit run app/ui/streamlit_app.py
```

By default, Streamlit runs at `http://localhost:8501`.

The UI will:

- ask for your **product idea** and optional context,
- call the `/generate` API,
- render tabs for **PRD**, **Architecture**, **ERD**, **API Spec**, **Tasks**,
- display **assumptions**,
- allow you to trigger **Export ZIP** (calls `/export`) and download the generated bundle.

---

## API Overview

### Health

- **GET** `/health`  
  Returns:

```json
{ "status": "ok", "app": "MVP Generator", "version": "0.1.0" }
```

### Generate

- **POST** `/generate`

Request body:

```json
{
  "product_idea": "Your idea here (min 10 chars)",
  "target_users": "Optional",
  "core_user_flow": "Optional",
  "constraints": "Optional",
  "output_stack": "FastAPI + SQLite + Streamlit"
}
```

Response body (simplified):

```json
{
  "generation_id": "uuid",
  "created_at": "ISO datetime",
  "result": {
    "title": "string",
    "summary": "string",
    "prd_lite": { "...": "..." },
    "architecture": { "...": "..." },
    "data_model": { "...": "..." },
    "api_spec": { "...": "..." },
    "tasks": { "...": "..." },
    "assumptions": ["..."]
  }
}
```

Always returns HTTP 200; if the LLM output is invalid, a safe fallback bundle is used and an assumption is added describing the fallback.

### History

- **GET** `/history?limit=5`

Returns a list of recent generations:

```json
[
  {
    "generation_id": "uuid",
    "created_at": "ISO datetime",
    "title": "string"
  }
]
```

### Export

- **POST** `/export`

Request body:

```json
{ "generation_id": "uuid" }
```

Returns a `application/zip` streaming response with filename:

`mvp_bundle_<generation_id>.zip`

ZIP contents:

- `README.md`
- `PRD.md`
- `ARCHITECTURE.md`
- `ERD.md`
- `API_SPEC.md`
- `TASKS.md`

Each file is readable Markdown and uses `mermaid` blocks where relevant.

---

## Development & Tests

Install dev dependencies:

```bash
pip install -r requirements.txt
```

Run tests:

```bash
pytest
```

Tests cover:

- schema validation & fallback behavior,
- prompt builder content (e.g., enforcing “Output ONLY JSON”),
- MVP service in **MOCK** mode (including DB persistence),
- core API endpoints in **MOCK** mode.

---

## Notes

- The app is intentionally small and demo-oriented.
- LOG files are written under `logs/` (created automatically) and ignored by git.
- SQLite DB is a local file (`mvp_generator.db`) in the project root, also gitignored.


