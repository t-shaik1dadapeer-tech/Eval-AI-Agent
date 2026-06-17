from pydantic import BaseModel, Field


class TransactionCreate(BaseModel):
    transaction_id: str = Field(..., min_length=1)
    user_id: str = Field(..., min_length=1)
    amount: float = Field(..., gt=0)
    merchant: str = Field(..., min_length=1)
    country: str = Field(..., min_length=2, max_length=2)


class TransactionAccepted(BaseModel):
    status: str = "accepted"
    transaction_id: str
