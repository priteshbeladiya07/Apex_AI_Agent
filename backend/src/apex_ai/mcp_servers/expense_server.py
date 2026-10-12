
from pathlib import Path
import sqlite3

from fastmcp import FastMCP

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "expenses.db"
CATEGORIES_PATH = BASE_DIR / "categories.json"

mcp = FastMCP("ExpenseTracker")


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT DEFAULT '',
                note TEXT DEFAULT ''
            )
        """)


init_db()


@mcp.tool()
def add_expense(
    date: str,
    amount: float,
    category: str,
    subcategory: str = "",
    note: str = "",
):
    """Add a new expense entry to the database."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            """
            INSERT INTO expenses
                (date, amount, category, subcategory, note)
            VALUES (?, ?, ?, ?, ?)
            """,
            (date, amount, category, subcategory, note),
        )
        return {"status": "ok", "id": cursor.lastrowid}


@mcp.tool()
def list_expenses(start_date: str, end_date: str):
    """List expenses within an inclusive date range."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            """
            SELECT id, date, amount, category, subcategory, note
            FROM expenses
            WHERE date BETWEEN ? AND ?
            ORDER BY id ASC
            """,
            (start_date, end_date),
        )
        columns = [item[0] for item in cursor.description]
        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]


@mcp.tool()
def summarize(
    start_date: str,
    end_date: str,
    category: str | None = None,
):
    """Summarize expenses by category within an inclusive date range."""
    query = """
        SELECT category, SUM(amount) AS total_amount
        FROM expenses
        WHERE date BETWEEN ? AND ?
    """
    params = [start_date, end_date]

    if category:
        query += " AND category = ?"
        params.append(category)

    query += " GROUP BY category ORDER BY category ASC"

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(query, params)
        columns = [item[0] for item in cursor.description]
        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]


@mcp.resource("expense://categories", mime_type="application/json")
def categories():
    """Return the configured expense categories."""
    return CATEGORIES_PATH.read_text(encoding="utf-8")


if __name__ == "__main__":
    mcp.run(transport="stdio")