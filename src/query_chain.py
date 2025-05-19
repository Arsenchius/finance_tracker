import yaml
from pathlib import Path

from langchain.chains import create_sql_query_chain
from langchain_community.utilities import SQLDatabase
from langchain_ollama import ChatOllama
from langchain.prompts import ChatPromptTemplate

PROMPT_DIR = Path(__file__).parent.parent / "prompts" / "v2"

with open(PROMPT_DIR / "system.yaml", "r", encoding="utf-8") as f:
    system_prompt = yaml.safe_load(f)["system_prompt"]

with open(PROMPT_DIR / "user.yaml", "r", encoding="utf-8") as f:
    user_prompt_template = yaml.safe_load(f)["user_prompt_template"]

prompt = ChatPromptTemplate.from_messages(
    [("system", system_prompt), ("user", user_prompt_template)]
)

llm = ChatOllama(model="gemma3:1b")
sql_generation_chain = prompt | llm

db = SQLDatabase.from_uri(
    "sqlite:///transactions.db",
    include_tables=["transactions"],
    sample_rows_in_table_info=1,
)

chain = create_sql_query_chain(llm, db)
