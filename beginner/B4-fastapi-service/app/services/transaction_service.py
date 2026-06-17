from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from app.models.transaction import Transaction, TransactionType
from app.schemas.transaction import TransactionCreate


class TransactionService:
    """In-memory transaction store with balance calculation."""

    def __init__(self) -> None:
        self._transactions: list[Transaction] = []

    def create_transaction(self, payload: TransactionCreate) -> Transaction:
        transaction = Transaction(
            id=uuid4(),
            type=payload.type,
            amount=payload.amount,
            description=payload.description,
            created_at=datetime.now(timezone.utc),
        )
        self._transactions.append(transaction)
        return transaction

    def list_transactions(self) -> list[Transaction]:
        return list(self._transactions)

    def get_transaction_by_id(self, transaction_id: UUID) -> Transaction | None:
        for transaction in self._transactions:
            if transaction.id == transaction_id:
                return transaction
        return None

    def get_balance(self) -> tuple[float, int]:
        balance = 0.0
        for transaction in self._transactions:
            if transaction.type == TransactionType.CREDIT:
                balance += transaction.amount
            else:
                balance -= transaction.amount
        return balance, len(self._transactions)

    def clear(self) -> None:
        """Reset store — used by tests."""
        self._transactions.clear()


transaction_service = TransactionService()
