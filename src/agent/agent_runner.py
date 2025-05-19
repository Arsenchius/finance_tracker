import asyncio

from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_community.chat_models import ChatOllama


async def run_agent():
    client = MultiServerMCPClient(
        {
            "DB executor": {
                "url": "http://localhost:8000/mcp",
                "transport": "streamable_http",
            }
        }
    )

    tools = await client.get_tools()
    llm = ChatOllama(model="gemma3:1b")
    agent = create_react_agent(llm, tools)

    response = await agent.ainvoke(
        {"messages": "Запиши в траты за вчера 700 рублей в макдональдс"}
    )
    print(response)


if __name__ == "__main__":
    asyncio.run(run_agent())
