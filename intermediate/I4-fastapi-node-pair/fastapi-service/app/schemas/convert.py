from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

SupportedCurrency = Literal["USD", "INR", "EUR"]


class ConvertRequest(BaseModel):
    amount: float = Field(..., gt=0)
    from_currency: SupportedCurrency
    to_currency: SupportedCurrency

    @field_validator("from_currency", "to_currency", mode="before")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        if isinstance(value, str):
            return value.upper()
        return value


class ConvertResponse(BaseModel):
    amount: float
    from_currency: str
    to_currency: str
    converted_amount: float


class ErrorResponse(BaseModel):
    detail: str
