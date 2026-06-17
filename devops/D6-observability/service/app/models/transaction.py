from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID


class TransactionType(str, Enum):
    CREDIT = "credit"
    DEBIT = "debit"


@dataclass
class Transaction:
    id: UUID
    type: TransactionType
    amount: float
    description: Optional[str]
    created_at: datetime
