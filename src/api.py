from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import logging
import traceback

from db import (
    add_transaction,
    delete_transaction,
    list_transactions,
    update_transaction as db_update_transaction,
)
from agent import agent

router = APIRouter()
logger = logging.getLogger(__name__)


class Transaction(BaseModel):
    user_id: str
    tx_type: str = Field(..., alias="type")
    amount: float
    category: str
    date: str


class NLQuery(BaseModel):
    user_id: str
    question: str


class UpdateTransactionRequest(BaseModel):
    user_id: str
    date: str
    updates: dict


@router.post("/add_transaction")
def add(data: Transaction):
    add_transaction(data.dict(by_alias=True))
    return {"status": "added"}


@router.delete("/delete_transaction")
def delete(user_id: str, category: str, date: str):
    delete_transaction(user_id, category, date)
    return {"status": "deleted"}


@router.get("/list_transactions")
def list_all(user_id: str):
    return list_transactions(user_id)


@router.post("/agent")
def run_agent(data: NLQuery):
    try:
        prompt = f"""
            Пользователь с ID {data.user_id} дал команду:
            {data.question}
        """
        result = agent.invoke({"input": prompt})

        for step in result.get("intermediate_steps", []):
            action, observation = step
            logger.info("=== ACTION ===")
            logger.info(f"Tool: {action.tool}")
            logger.info(f"Input: {action.tool_input}")
            logger.info(f"Observation: {observation}")
            logger.info("==============")

        return {
            "answer": result.get("output"),
            "log": result.get("log"),
            "inputs_used": [
                step[0].tool_input for step in result.get("intermediate_steps", [])
            ],
        }
    except Exception as e:
        logger.exception("Agent invocation failed")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/update_transaction")
def update_transaction(data: UpdateTransactionRequest):
    db_update_transaction(data.user_id, data.date, data.updates)
    return {"status": "updated"}
