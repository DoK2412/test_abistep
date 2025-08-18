from pydantic import BaseModel
from fastapi import Query


class User(BaseModel):
    name: str = Query(description="Имя пользователя"),
    email: str = Query(description="Email пользователя"),
    balance: float = Query(default=0, description="Баланс пользователя")


class Transfer(BaseModel):
    from_user_id: int = Query(description="Id кошелька для списания"),
    to_user_id: int = Query(description="Id кошелька для пополнения"),
    amount: float = Query(description="Сумма для обработки")