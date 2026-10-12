# Apex AI Agent
 
**Apex AI Agent** is a modular, tool-using AI assistant built with **LangGraph**, **MCP (Model Context Protocol)**, **FastAPI**, **React**, and **PostgreSQL**. It offers a single, minimalist chat interface through which the agent can answer questions, call connected tools, and be extended with additional MCP servers.
 
The chat experience is deliberately separated from individual integrations: new capabilities are added by registering MCP servers and controlling their tools through the backend.
 
---
 
## Table of contents
 
- [Key features](#key-features)
- [Architecture](#architecture)
- [Technology stack](#technology-stack)
- [Repository structure](#repository-structure)
- [MCP servers and status](#mcp-servers-and-status)
- [PostgreSQL chat history](#postgresql-chat-history)
- [Getting started](#getting-started)
- [Docker Hub images](#docker-hub-images)
- [Adding more MCP servers](#adding-more-mcp-servers)
---
 
## Key features
 
- **Single chat interface**: a minimalist React UI with a conversation sidebar.
- **Tool-using agent**: LangGraph decides when to answer directly and when to call a tool.
- **Pluggable tools via MCP**: add or remove capabilities by registering MCP servers, with no changes to the chat UI.
- **Permission-controlled tools**: a registry and permission layer restricts which tools the agent may call.
- **Persistent chat history**: conversations and messages are stored in PostgreSQL and reloaded in the sidebar.
- **Containerized**: separate backend and frontend images, orchestrated with Docker Compose.
---
 
## Architecture
 
### System overview
 
```mermaid
flowchart TB
    USER(["User"])
 
    subgraph CLIENT["Client layer"]
        UI["React + Vite + TypeScript<br/>Chat UI and conversation sidebar"]
    end
 
    subgraph BACKEND["Backend layer · FastAPI"]
        API["API routes<br/>api/"]
        SVC["Chat service and business logic<br/>chat_service.py · services/"]
        DBL["Persistence layer<br/>database/"]
    end
 
    subgraph AGENTL["Agent layer · LangGraph"]
        AGENT["Agent orchestrator<br/>agents/"]
        LLM["LLM integration<br/>llm/"]
    end
 
    subgraph TOOLL["Tool layer · MCP"]
        MGR["MCP client manager<br/>mcp/"]
        REG["Tool registry and<br/>permission checks"]
    end
 
    subgraph SERVERS["MCP servers"]
        EXP["Expense Tracker MCP<br/>remote · FastMCP"]
        MATH["Math MCP<br/>add · subtract · multiply · divide"]
        MAN["Manim MCP<br/>animation generation"]
        SEARCH["Research / Web Search MCP<br/>optional"]
    end
 
    PG[("PostgreSQL<br/>conversations and messages")]
    MISTRAL["Mistral API<br/>codestral-2508"]
 
    USER <--> UI
    UI <-->|"HTTP / REST"| API
    API --> SVC
    SVC <--> AGENT
    SVC <--> DBL
    DBL <--> PG
    AGENT <--> LLM
    LLM <--> MISTRAL
    AGENT <--> MGR
    MGR <--> REG
    REG <--> EXP
    REG <--> MATH
    REG <--> MAN
    REG -.-> SEARCH
```
 
### Request lifecycle
 
```mermaid
sequenceDiagram
    autonumber
    actor U as User
    participant UI as React Chat UI
    participant API as FastAPI Backend
    participant DB as PostgreSQL
    participant AG as LangGraph Agent
    participant LLM as Mistral API
    participant MCP as MCP Client Manager
    participant SRV as MCP Server
 
    U->>UI: Send message
    UI->>API: Chat request
    API->>DB: Save user message
    API->>AG: Run agent with conversation context
    AG->>LLM: Interpret request
    LLM-->>AG: Direct answer or tool call
 
    alt Tool call needed
        AG->>MCP: Request tool call
        MCP->>MCP: Check registry and permissions
        MCP->>SRV: Invoke allowed tool
        SRV-->>MCP: Tool result
        MCP-->>AG: Return result
        AG->>LLM: Compose answer using tool result
        LLM-->>AG: Final answer
    end
 
    AG-->>API: Final response
    API->>DB: Save assistant message
    API-->>UI: Return response
    UI-->>U: Display answer
```
 
---
 
## Technology stack
 
| Layer | Technology | Responsibility |
|---|---|---|
| Frontend | React, Vite, TypeScript | Chat interface and conversation sidebar |
| Backend API | Python, FastAPI | API endpoints and application coordination |
| Agent orchestration | LangGraph | Agent flow, model calls, and tool execution |
| Language model | Mistral API | Interprets requests and generates responses (model setting: `codestral-2508`) |
| Tool protocol | MCP / FastMCP | Connects the agent to independently exposed tools |
| Chat storage | PostgreSQL | Persists conversations and messages |
| Python tooling | `uv`, `pyproject.toml` | Dependency and environment management |
| Containers | Docker, Docker Compose | Packages and runs the frontend and backend |
 
---
 
## Repository structure
 
```text
ApeX AI/
├── backend/
│   ├── src/
│   │   ├── apex_ai/
│   │   │   ├── agents/            # LangGraph agent definitions and orchestration
│   │   │   ├── api/               # FastAPI routes (chat, conversations)
│   │   │   ├── core/              # Core configuration and shared utilities
│   │   │   ├── database/          # PostgreSQL connection, sessions, and models
│   │   │   ├── llm/               # Language model (Mistral) integration
│   │   │   ├── mcp/               # MCP client manager, tool registry, permissions
│   │   │   ├── mcp_servers/       # Locally hosted MCP servers (e.g. math, Manim)
│   │   │   ├── schemas/           # Pydantic request/response schemas
│   │   │   ├── services/          # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── chat_service.py    # Chat orchestration service
│   │   │   └── main.py            # FastAPI application entry point
│   │   ├── migrations/            # Database migrations
│   │   └── tests/                 # Backend tests
│   ├── Dockerfile                 # Backend image
│   └── uv.lock                    # Locked backend dependencies
│
├── frontend/
│   ├── src/                       # React + TypeScript source
│   ├── .env.example               # Template for frontend environment variables
│   ├── Dockerfile                 # Frontend image
│   ├── index.html
│   ├── package.json
│   ├── package-lock.json
│   ├── tsconfig.json
│   ├── tsconfig.app.json
│   ├── tsconfig.node.json
│   └── vite.config.ts             # Vite configuration
│
├── docs/                          # Project documentation
│
├── .gitignore
├── .python-version                # Pinned Python version
├── backend-requirements.txt       # Backend dependency list
├── expense-requirements.txt       # Dependencies for the expense MCP environment
├── compose.yml                    # Docker Compose services
├── package.json
├── package-lock.json
├── pyproject.toml                 # Python project configuration
├── uv.lock
└── README.md
```
 
**Local-only files (never commit):** `.env`, `frontend/.env.local`, `.venv/`, `.venv-expense/`, `frontend/node_modules/`, and `__pycache__/`. Make sure all of them are listed in `.gitignore`.
 
> Folder descriptions above reflect each folder's role as named in the project layout. Adjust a comment if a folder's contents differ in your checkout.
 
---
 
## MCP servers and status
 
A server should be described as **live** only when its process or endpoint is reachable, the backend's MCP client connects without errors, and the agent discovers its tools. The table below documents the intended integrations; it is not a live health check.
 
| MCP integration | Purpose / tools | Status |
|---|---|---|
| **Expense Tracker MCP** | Remote FastMCP service for adding expenses, listing expenses, and summarizing spending by category. It maintains its own expense data. | Remote endpoint configured. Confirm reachability and tool discovery in backend logs. |
| **Math MCP** | Arithmetic: addition, subtraction, multiplication, and division. Division must validate a zero denominator and return a clear error. | Count as live only once the server is running, registered, and its tools are discovered. |
| **Manim MCP** | Exposes `execute_manim_code` to generate mathematical and educational animations. Requires the Manim runtime and its dependencies. | Implemented locally. Running state must be verified. |
| **Research / Web Search MCP** | Optional search/research tools (e.g. `web_search`). | Optional. Not counted as live without a successful connection. |
 
### Verifying a server
 
1. The process is running, or the remote endpoint is reachable.
2. The backend establishes an MCP client connection without errors.
3. The server's tools appear in the tool registry.
4. A safe test call returns the expected result.
Check `docker compose logs -f backend` for connection and tool-discovery messages to confirm how many servers are actually live.
 
---
 
## PostgreSQL chat history
 
PostgreSQL stores each user's conversations and messages so previous chats can be reloaded in the sidebar after a page refresh.
 
```mermaid
flowchart LR
    subgraph FE["Frontend"]
        SIDEBAR["Conversation sidebar"]
        CHATUI["Chat window"]
    end
 
    subgraph BE["FastAPI backend"]
        ROUTES["api/ routes"]
        SVC["services/ · chat_service.py"]
        DBL["database/<br/>sessions and models"]
    end
 
    PG[("PostgreSQL<br/>conversations and messages")]
 
    SIDEBAR -->|"List and load conversations"| ROUTES
    CHATUI -->|"Send message"| ROUTES
    ROUTES --> SVC
    SVC --> DBL
    DBL <-->|"Read and write"| PG
```
 
- The frontend retrieves history **only through the backend API** and never connects to PostgreSQL directly.
- Schema changes are managed through the `backend/src/migrations/` directory.
- Table definitions live in `backend/src/apex_ai/database/`. Treat the models and migrations as the source of truth for the schema.
---
 
## Getting started
 
### Prerequisites
 
- Docker and Docker Compose (for the containerized setup)
- Python (version pinned in `.python-version`) and [`uv`](https://docs.astral.sh/uv/) for local backend development
- Node.js and npm for local frontend development
- A Mistral API key and a PostgreSQL database
### 1. Configure environment variables
 
Create your private `.env` file in the project root and `frontend/.env.local` for the frontend. Use `frontend/.env.example` as the template for frontend variables. **Never commit these files or share their contents.**
 
### 2. Run with Docker (recommended)
 
```mermaid
flowchart LR
    BROWSER(["Browser"])
 
    subgraph COMPOSE["Docker Compose · compose.yml"]
        FE["Frontend container<br/>pritesh077/apex-ai-frontend"]
        BE["Backend container<br/>pritesh077/apex-ai-backend"]
    end
 
    PG[("PostgreSQL")]
    LOCAL["Local MCP servers<br/>math · Manim"]
    EXP["Remote Expense Tracker MCP"]
    MIS["Mistral API"]
 
    BROWSER -->|"Loads app"| FE
    BROWSER -->|"API requests"| BE
    BE --> PG
    BE --> LOCAL
    BE --> EXP
    BE --> MIS
```
 
PostgreSQL may run as a Compose service or as an external instance; check `compose.yml` for the actual setup.
 
Run from the folder containing `compose.yml`:
 
```powershell
# Pull images referenced by the Compose configuration
docker compose pull
 
# Start the services in the background
docker compose up -d
 
# Check service status
docker compose ps
 
# Follow logs
docker compose logs -f
 
# Stop and remove containers
docker compose down
```
 
If `compose.yml` uses `build:` instead of `image:`, Compose builds from source rather than pulling from Docker Hub. Use `docker compose up -d --build` in that case. Check the port mappings in `compose.yml` before opening the app in your browser.
 
### 3. Run locally (development)
 
**Backend**
 
```powershell
uv sync
uv run uvicorn apex_ai.main:app --reload --app-dir backend/src
```
 
**Frontend**
 
```powershell
cd frontend
npm install
npm run dev
```
 
Adjust the commands if your entry point or scripts differ.
 
---
 
## Docker Hub images
 
The frontend and backend are published as two separate images under the Docker Hub account `pritesh077`.
 
| Component | Image | Repository |
|---|---|---|
| Backend | `pritesh077/apex-ai-backend:latest` | <https://hub.docker.com/r/pritesh077/apex-ai-backend> |
| Frontend | `pritesh077/apex-ai-frontend:latest` | <https://hub.docker.com/r/pritesh077/apex-ai-frontend> |
 
```powershell
docker pull pritesh077/apex-ai-backend:latest
docker pull pritesh077/apex-ai-frontend:latest
```
 
### Publishing images
 
Tag the local images and push them:
 
```powershell
# Backend
docker tag apexai-backend:latest pritesh077/apex-ai-backend:latest
docker push pritesh077/apex-ai-backend:latest
 
# Frontend
docker tag apexai-frontend:latest pritesh077/apex-ai-frontend:latest
docker push pritesh077/apex-ai-frontend:latest
```
 
If an upload times out, rerun the same `docker push` command; Docker reuses layers that were already uploaded. Afterwards, confirm that the `latest` tag appears in the correct Docker Hub repository. A local image or partial upload does not confirm a successful publish.
 
---
 
## Adding more MCP servers
 
Apex AI Agent is not tied to a fixed list of integrations. New MCP servers can provide file operations, database queries, calendars, documentation search, analytics, coding helpers, and more, provided the server and its authorization are implemented.
 
The practical limit on the number of servers depends on compute and memory, open connections, latency, API rate limits, model context size, tool-description size, operational complexity, and security. More servers are not automatically better, so expose only tools that are useful and safe.
 
**Onboarding checklist**
 
1. Implement or select an MCP server and document the tools it exposes.
2. Register it in `backend/src/apex_ai/mcp/` (client manager and tool registry). Place locally hosted servers in `backend/src/apex_ai/mcp_servers/`.
3. Apply an explicit tool allowlist and least-privilege permissions.
4. Configure credentials privately, outside source control.
5. Test the connection, tool discovery, success paths, invalid inputs, timeouts, and error handling.
6. Update the architecture diagram and status table once the server's role and state are known.
---
 
**Apex AI Agent**: one chat interface, LangGraph orchestration, PostgreSQL-backed chat history, and an extensible MCP tool ecosystem.
 
