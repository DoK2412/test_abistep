from pydantic import BaseModel

class AllUser(BaseModel):
    id: int
    name: str
    email: str
    balance: float