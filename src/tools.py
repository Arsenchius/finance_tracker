import requests
from langchain.tools import tool

from query_chain import sql_generation_chain


@tool
def add_transaction_tool(
    user_id: str, tx_type: str, amount: float, category: str, date: str
):
    """Добавляет транзакцию (доход или расход). Аргументы: user_id — ID пользователя, tx_type — 'income' или 'expense', amount — сумма, category — категория (например, 'еда', 'транспорт'), date — дата (например, '2025-05-14' или 'вчера')."""
    data = {
        "user_id": user_id,
        "type": tx_type,
        "amount": amount,
        "category": category,
        "date": date,
    }
    response = requests.post("http://localhost:8000/add_transaction", json=data)
    return response.json()


@tool
def delete_transaction_tool(user_id: str, category: str, date: str):
    """Удаляет транзакцию по user_id, дате и категории."""
    response = requests.delete(
        "http://localhost:8000/delete_transaction",
        params={"user_id": user_id, "category": category, "date": date},
    )
    return response.json()


@tool
def update_transaction_tool(user_id: str, date: str, updates: dict):
    """Обновляет поля транзакции по user_id и дате. updates может содержать amount или category."""
    response = requests.put(
        "http://localhost:8000/update_transaction",
        json={"user_id": user_id, "date": date, "updates": updates},
    )
    return response.json()


@tool
def analyze_query_tool(user_id: str, question: str):
    """Отвечает на аналитический вопрос по транзакциям пользователя, генерируя SQL-запрос."""
    full_prompt = {"user_id": user_id, "input_text": question}
    return sql_generation_chain.run(full_prompt)
