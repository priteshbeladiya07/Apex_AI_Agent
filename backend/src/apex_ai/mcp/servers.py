from pathlib import Path
import os
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[4]

MCP_VENV_PYTHON = (
    PROJECT_ROOT
    / ".venv-expense"
    / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
)
MCP_PYTHON = (
    str(MCP_VENV_PYTHON)
    if MCP_VENV_PYTHON.is_file()
    else sys.executable
)

EXPENSE_SERVER = (
    PROJECT_ROOT
    / "backend"
    / "src"
    / "apex_ai"
    / "mcp_servers"
    / "expense_server.py"
)

RESEARCH_SERVER = (
    PROJECT_ROOT
    / "backend"
    / "src"
    / "apex_ai"
    / "mcp_servers"
    / "research_server.py"
)

ARITH_SERVER = (
    PROJECT_ROOT
    / "backend"
    / "src"
    / "apex_ai"
    / "mcp_servers"
    / "arith_server.py"
)

MANIM_SERVER = (
    PROJECT_ROOT
    / "backend"
    / "src"
    / "apex_ai"
    / "mcp_servers"
    / "manim_server.py"
)



SERVERS = {
    "EXPENSE": {
        "transport": "stdio",
        "command": MCP_PYTHON,
        "args": [str(EXPENSE_SERVER)],
    },
    "RESEARCH": {
        "transport": "stdio",
        "command": MCP_PYTHON,
        "args": [str(RESEARCH_SERVER)],
    },
    "ARITH": {
        "transport": "stdio",
        "command": MCP_PYTHON,
        "args": [str(ARITH_SERVER)],
    },
    "MANIM": {
        "transport": "stdio",
        "command": MCP_PYTHON,
        "args": [str(MANIM_SERVER)],
    },
    
}