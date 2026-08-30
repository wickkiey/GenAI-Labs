from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path

try:
    from .registry import register_tool
except ImportError:
    from registry import register_tool

DB_PATH = (Path(__file__).resolve().parents[2] / "data" / "labs.db").resolve()

_TABLE_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_SELECT_ONLY = re.compile(r"^\s*SELECT\b", re.IGNORECASE)

LIST_TABLES_SCHEMA = {
    "type": "function",
    "function": {
        "name": "list_tables",
        "description": "List all table names in the labs database.",
        "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
    },
}

DESCRIBE_TABLE_SCHEMA = {
    "type": "function",
    "function": {
        "name": "describe_table",
        "description": "Describe the columns of a table in the labs database.",
        "parameters": {
            "type": "object",
            "properties": {"table": {"type": "string", "description": "Table name."}},
            "required": ["table"],
            "additionalProperties": False,
        },
    },
}

QUERY_DATABASE_SCHEMA = {
    "type": "function",
    "function": {
        "name": "query_database",
        "description": "Run a single read-only SELECT query against the labs database.",
        "parameters": {
            "type": "object",
            "properties": {"query": {"type": "string", "description": "A single SELECT statement."}},
            "required": ["query"],
            "additionalProperties": False,
        },
    },
}


def _ensure_db() -> None:
    if DB_PATH.exists():
        return
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript(
            """
            CREATE TABLE departments (id INTEGER PRIMARY KEY, name TEXT NOT NULL);
            CREATE TABLE employees (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                department_id INTEGER NOT NULL,
                salary REAL NOT NULL
            );
            CREATE TABLE sales (
                id INTEGER PRIMARY KEY,
                employee_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                quarter TEXT NOT NULL
            );
            INSERT INTO departments (id, name) VALUES (1, 'Sales'), (2, 'Engineering'), (3, 'Marketing');
            INSERT INTO employees (id, name, department_id, salary) VALUES
                (1, 'Alice', 1, 65000),
                (2, 'Bob', 1, 60000),
                (3, 'Carol', 2, 90000),
                (4, 'Dave', 2, 95000),
                (5, 'Erin', 3, 55000);
            INSERT INTO sales (id, employee_id, amount, quarter) VALUES
                (1, 1, 12000, 'Q1'),
                (2, 2, 15000, 'Q1'),
                (3, 1, 13000, 'Q2'),
                (4, 2, 9000, 'Q2');
            """
        )
        conn.commit()
    finally:
        conn.close()


@register_tool(LIST_TABLES_SCHEMA)
def list_tables() -> str:
    _ensure_db()
    conn = sqlite3.connect(DB_PATH)
    try:
        rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    finally:
        conn.close()
    return ", ".join(row[0] for row in rows)


@register_tool(DESCRIBE_TABLE_SCHEMA)
def describe_table(table: str) -> str:
    _ensure_db()
    if not _TABLE_NAME.match(table):
        return "Error: invalid table name"
    conn = sqlite3.connect(DB_PATH)
    try:
        rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    finally:
        conn.close()
    if not rows:
        return f"Error: table '{table}' not found"
    return ", ".join(f"{row[1]} ({row[2]})" for row in rows)


@register_tool(QUERY_DATABASE_SCHEMA)
def query_database(query: str) -> str:
    _ensure_db()
    stripped = query.strip().rstrip(";")
    if not _SELECT_ONLY.match(stripped) or ";" in stripped:
        return "Error: only a single read-only SELECT statement is allowed"
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA query_only = ON")  # defense in depth against writes
    try:
        cursor = conn.execute(stripped)
        rows = cursor.fetchall()
        columns = [d[0] for d in cursor.description] if cursor.description else []
    except sqlite3.Error as error:
        return f"Error: {error}"
    finally:
        conn.close()
    return json.dumps({"columns": columns, "rows": rows})
