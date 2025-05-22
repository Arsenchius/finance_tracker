import uuid

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.memory import InMemorySaver

from tools import (
    add_transaction,
    update_transaction,
    delete_transaction,
    query_analytics,
    summarize_sql_result,
)

SYSTEM_PROMPT = """
    Ты — финансовый помощник. Помогаешь пользователю вести учёт расходов и доходов,
    отвечаешь на вопросы о тратах, доходах, категориях и периодах.
    Ты можешь добавлять записи, изменять их, удалять (только после подтверждения),
    а также выполнять аналитические запросы к базе данных и возвращать краткие, понятные ответы.

    Если запрос связан с удалением данных — обязательно уточни, действительно ли пользователь хочет это сделать.
    Если пользователь использует слова вроде «вчера», «прошлый месяц», ты обязан сам преобразовать их в конкретную дату в формате YYYY-MM-DD.

    Примеры запросов пользователя и как ты на них реагируешь:

    Пример 1:
    Пользователь: Запиши трату за вчера 700 рублей на продукты
    Ты вызываешь инструмент `add_transaction` с такими параметрами:
    {
    "category": "продукты",
    "amount": 700,
    "date": "2025-05-21",  // если сегодня 22 мая
    "type": "expense",
    "user_id": "user_123"
    }

    Пример 2:
    Пользователь: Удали трату в пятерочке за 10 мая
    Ты вызываешь `delete_transaction`:
    {
    "category": "пятерочка",
    "date": "2025-05-10",
    "user_id": "user_123",
    "confirm": false
    }

    Пример 3:
    Пользователь: Сколько я тратил на еду за апрель?
    Ты вызываешь `query_analytics` с SQL-запросом:
    SELECT SUM(amount) FROM transactions WHERE user_id = '{user_id}' AND category = 'еда' AND strftime('%m', date) = '04';

    Затем ты передаёшь результат в `summarize_sql_result`, чтобы сформулировать краткий человекочитаемый ответ.
"""


class FinanceAgent:
    def __init__(self):
        # self.model = ChatOllama(model="llama3", temperature=0.1)
        self._model = ChatOpenAI(
            api_key="ollama",
            model="phi4-mini:3.8b",
            base_url="http://localhost:11434/v1",
        )
        self._agent = create_react_agent(
            self._model,
            tools=[
                add_transaction,
                update_transaction,
                delete_transaction,
                query_analytics,
                summarize_sql_result,
            ],
            checkpointer=InMemorySaver(),
        )
        self._config: RunnableConfig = {"configurable": {"thread_id": uuid.uuid4().hex}}
        self._system_prompt = SystemMessage(content=SYSTEM_PROMPT)

    def invoke(self, content: str) -> str:
        response = self._agent.invoke(
            {"messages": [self._system_prompt, HumanMessage(content=content)]},
            config=self._config,
        )
        return response["messages"][-1].content


if __name__ == "__main__":
    agent = FinanceAgent()
    print("Финансовый помощник запущен. Введите ваш запрос:")
    while True:
        try:
            query = input("Вы: ")
            response = agent.invoke(f"Пользователь с ID user_1 дал команду: {query}")
            print(f"Агент: {response}")
        except KeyboardInterrupt:
            print("До свидания!")
            break
