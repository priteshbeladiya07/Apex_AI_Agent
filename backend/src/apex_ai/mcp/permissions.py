from dataclasses import dataclass
from typing import Literal


Permission = Literal["read", "write", "delete", "export", "research"]


@dataclass(frozen=True)
class ToolPolicy:
    permission: Permission
    requires_confirmation: bool = False


TOOL_POLICIES: dict[str, ToolPolicy] = {
    "expense_list_expenses": ToolPolicy("read"),
    "expense_get_spending_summary": ToolPolicy("read"),
    "expense_add_expense": ToolPolicy("write", True),
    "expense_update_expense": ToolPolicy("write", True),
    "expense_delete_expense": ToolPolicy("delete", True),
    "sheets_read_data": ToolPolicy("read"),
    "sheets_add_data": ToolPolicy("write", True),
    "sheets_update_data": ToolPolicy("write", True),
    "sheets_delete_data": ToolPolicy("delete", True),
    "sheets_export_data": ToolPolicy("export", True),
    "research_search_web": ToolPolicy("research"),
}


def get_tool_policy(tool_name: str) -> ToolPolicy:
    if tool_name not in TOOL_POLICIES:
        raise PermissionError(f"Unknown tool: {tool_name}")
    return TOOL_POLICIES[tool_name]


def check_tool_permission(
    tool_name: str,
    user_permissions: set[str],
) -> bool:
    policy = get_tool_policy(tool_name)
    return policy.permission in user_permissions


def require_tool_permission(
    tool_name: str,
    user_permissions: set[str],
) -> None:
    if not check_tool_permission(tool_name, user_permissions):
        policy = get_tool_policy(tool_name)
        raise PermissionError(
            f"Access denied. '{tool_name}' requires "
            f"'{policy.permission}' permission."
        )


def requires_confirmation(tool_name: str) -> bool:
    return get_tool_policy(tool_name).requires_confirmation