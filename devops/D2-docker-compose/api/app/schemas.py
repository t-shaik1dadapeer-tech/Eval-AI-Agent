from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class TransactionCreate(BaseModel):
    transaction_id: str = Field(..., min_length=1, max_length=64)
    amount: float = Field(..., gt=0)


class TransactionResponse(BaseModel):
    id: int
    transaction_id: str
    amount: float
    status: str
    created_at: datetime

    @classmethod
    def from_row(cls, row: dict) -> "TransactionResponse":
        amount = row["amount"]
        if isinstance(amount, Decimal):
            amount = float(amount)
        return cls(
            id=row["id"],
            transaction_id=row["transaction_id"],
            amount=amount,
            status=row["status"],
            created_at=row["created_at"],
        )


class TransactionAccepted(BaseModel):
    status: str = "accepted"
    transaction_id: str
