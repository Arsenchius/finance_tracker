from langchain.agents import initialize_agent
from langchain.agents.agent_types import AgentType
from langchain_ollama import ChatOllama

from tools import (
    add_transaction_tool,
    delete_transaction_tool,
    update_transaction_tool,
    analyze_query_tool,
)


llm = ChatOllama(model="gemma3:1b")

tools = [
    add_transaction_tool,
    delete_transaction_tool,
    update_transaction_tool,
    analyze_query_tool,
]

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
)
