import sqlite3

from langchain_core.tools import tool


@tool
def add_transaction(category: str, amount: float, date: str, type: str, user_id: str):
    """
    Добавляет новую финансовую транзакцию пользователя в базу данных.

    Args:
        category: Категория траты или дохода (например, 'продукты', 'зарплата').
        amount: Сумма транзакции в рублях.
        date: Дата транзакции (в формате YYYY-MM-DD).
        type: Тип операции: 'income' (доход) или 'expense' (расход).
        user_id: Уникальный идентификатор пользователя.
    """
    with sqlite3.connect("transactions.db") as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO transactions (user_id, category, amount, date, type)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, category, amount, date, type),
        )
        conn.commit()
    return f"Добавлена транзакция: {type} {amount}₽, {category}, {date}"


@tool
def update_transaction(
    old_category: str, new_category: str, amount: float, user_id: str
):
    """
    Обновляет транзакцию пользователя, изменяя категорию и сумму.

    Args:
        old_category: Старая категория, которую нужно заменить.
        new_category: Новое значение категории.
        amount: Новая сумма транзакции в рублях.
        user_id: Уникальный идентификатор пользователя.
    """
    with sqlite3.connect("transactions.db") as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE transactions
            SET category = ?, amount = ?
            WHERE user_id = ? AND category = ?
            """,
            (new_category, amount, user_id, old_category),
        )
        conn.commit()
    return f"Обновлена транзакция категории {old_category} → {new_category}, сумма {amount}₽"


@tool
def delete_transaction(category: str, date: str, user_id: str, confirm: bool = False):
    """
    Удаляет транзакцию пользователя по категории и дате.
    Требует подтверждения через параметр confirm=True.

    Args:
        category: Категория транзакции.
        date: Дата транзакции (в формате YYYY-MM-DD).
        user_id: Уникальный идентификатор пользователя.
        confirm: Флаг подтверждения удаления (True — подтвердить удаление).
    """
    if not confirm:
        return (
            "Пожалуйста, подтвердите удаление, повторив запрос с фразой 'подтверждаю'"
        )
    with sqlite3.connect("transactions.db") as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            DELETE FROM transactions
            WHERE user_id = ? AND category = ? AND DATE(date) = DATE(?)
            """,
            (user_id, category, date),
        )
        conn.commit()
    return f"Удалена транзакция {category} за {date}"


@tool
def query_analytics(sql_query: str, user_id: str):
    """
    Выполняет безопасный SELECT SQL-запрос к базе данных транзакций пользователя.
    Запрещены опасные ключевые слова (DROP, TRUNCATE, ALTER).

    Args:
        sql_query: SQL-запрос, содержащий '{user_id}' в качестве плейсхолдера.
        user_id: Уникальный идентификатор пользователя.
    """
    lowered = sql_query.lower()
    if any(kw in lowered for kw in ["drop", "truncate", "alter"]):
        raise ValueError("Опасные SQL-команды запрещены")
    query = sql_query.replace("{user_id}", f"'{user_id}'")
    with sqlite3.connect("transactions.db") as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]


@tool
def summarize_sql_result(sql_result: list, user_query: str) -> str:
    """
    Преобразует результат SQL-запроса в человекочитаемый текст.

    Args:
        sql_result: Результат выполнения SQL-запроса (список словарей).
        user_query: Оригинальный запрос пользователя для контекста ответа.

    Returns:
        Текстовое описание результата.
    """
    if not sql_result:
        return "По вашему запросу данных не найдено."
    if isinstance(sql_result, list) and isinstance(sql_result[0], dict):
        keys = sql_result[0].keys()
        rows = ["; ".join(f"{k}: {r[k]}" for k in keys) for r in sql_result]
        return f"Результаты по запросу '{user_query}':\n" + "\n".join(rows)
    return f"Результат: {sql_result}"
