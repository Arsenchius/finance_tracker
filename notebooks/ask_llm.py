from langchain_ollama import ChatOllama
from langchain_core.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
)
from langchain_core.output_parsers import StrOutputParser

base_url = "http://localhost:11434"
model = "gemma3:1b"

llm = ChatOllama(base_url=base_url, model=model)

system = SystemMessagePromptTemplate.from_template(
    "Ты — полезный AI-ассистент, который отвечает на вопросы пользователя на основе предоставленного контекста."
)

prompt = """Отвечай на вопрос пользователя ТОЛЬКО на основе предоставленного контекста.
Если ты не знаешь ответа, просто скажи: «Я не знаю».

### Контекст:
{context}

### Вопрос:
{question}

### Ответ:"""

prompt = HumanMessagePromptTemplate.from_template(prompt)

messages = [system, prompt]
template = ChatPromptTemplate(messages)

qna_chain = template | llm | StrOutputParser()


def ask_llm(context, question):
    return qna_chain.invoke({"context": context, "question": question})
