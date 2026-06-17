from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.models.transaction import TransactionType


class TransactionCreate(BaseModel):
    type: TransactionType
    amount: float = Field(
        ..., gt=0, description="Transaction amount; must be greater than zero"
    )
    description: Optional[str] = Field(default=None, max_length=500)

    @field_validator("description")
    @classmethod
    def strip_description(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None


class TransactionResponse(BaseModel):
    id: UUID
    type: TransactionType
    amount: float
    description: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class BalanceResponse(BaseModel):
    balance: float
    transaction_count: int
