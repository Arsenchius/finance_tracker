import sqlite3

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel

from db import init_db

mcp = FastMCP("DB executor")
init_db()

FORBIDDEN_SQL_KEYWORDS = ["truncate", "delete", "drop"]


class SQLQuery(BaseModel):
    user_id: str
    query: str


@mcp.tool()
def execute_sql_query(input: SQLQuery):
    lowered_query = input.query.lower()
    if any(keyword in lowered_query for keyword in FORBIDDEN_SQL_KEYWORDS):
        raise ValueError(
            "Запрос содержит запрещённые SQL-операции (truncate, delete, drop)"
        )

    query = input.query.replace("{user_id}", f"'{input.user_id}'")

    with sqlite3.connect("transactions.db") as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            if query.strip().lower().startswith("select"):
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                return [dict(zip(columns, row)) for row in rows]
            else:
                conn.commit()
                return {"status": "ok"}
        except Exception as e:
            raise ValueError(f"Ошибка выполнения SQL: {str(e)}")


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
