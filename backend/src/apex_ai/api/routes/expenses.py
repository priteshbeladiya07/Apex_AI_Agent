from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from apex_ai.services.expense_service import ExpenseService

router = APIRouter()
expense_service = ExpenseService()


class ExpenseToolRequest(BaseModel):
    arguments: dict[str, Any] = Field(default_factory=dict)


@router.get("/tools")
async def list_expense_tools():
    try:
        tools = await expense_service.list_tools()
        return {"tools": tools}

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="Could not connect to the Expense Tracker MCP server",
        ) from exc


@router.post("/tools/{tool_name}")
async def execute_expense_read_tool(
    tool_name: str,
    payload: ExpenseToolRequest,
):
    try:
        result = await expense_service.execute_tool(
            tool_name=tool_name,
            arguments=payload.arguments,
            user_permissions={"read"},
            confirmed=False,
        )

        return {"tool": tool_name, "result": result}

    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc

    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="Expense Tracker tool execution failed",
        ) from exc