# Apex AI

Apex AI contains a Vite/React chat frontend and a FastAPI backend.

## Prerequisites

- Node.js and npm
- Python 3.12 and [uv](https://docs.astral.sh/uv/)
- PostgreSQL, configured with an async SQLAlchemy URL in the root `.env`
- A Mistral API key to send messages to the AI

The backend starts its Expense Tracker and web Research MCP servers as
subprocesses. Their tools are controlled by the comma-separated
`MCP_ALLOWED_TOOLS` setting. Use discovered tool names such as `add_expense`,
`list_expenses`, `summarize`, and `search_web`, or their prefixed equivalents.

## Setup

From the repository root, install Python dependencies without installing the
project as a package:

```powershell
uv sync --no-install-project
```

Install frontend dependencies:

```powershell
npm --prefix frontend install
```

Create a root `.env` with your backend settings, including `DATABASE_URL`,
`MISTRAL_API_KEY`, `TAVILY_API_KEY`, and `MCP_ALLOWED_TOOLS` (include
`search_web` to enable web research). Do not commit credentials.

## Run

Start the backend in one terminal:

```powershell
.venv\Scripts\python.exe -m uvicorn apex_ai.main:app --app-dir backend\src --reload
```

Start the frontend in another terminal:

```powershell
npm run dev
```

The frontend runs in demo mode by default and can be used without a backend.
The backend API documentation is available at `http://127.0.0.1:8000/docs`.

## Build

Build and type-check the frontend from the repository root:

```powershell
npm run build
```