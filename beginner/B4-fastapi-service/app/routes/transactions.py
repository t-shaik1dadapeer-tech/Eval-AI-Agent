from fastapi import APIRouter, status

from app.schemas.transaction import (
    BalanceResponse,
    TransactionCreate,
    TransactionResponse,
)
from app.services.transaction_service import transaction_service

router = APIRouter(tags=["transactions"])


@router.post(
    "/transactions",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a transaction",
)
def create_transaction(payload: TransactionCreate) -> TransactionResponse:
    transaction = transaction_service.create_transaction(payload)
    return TransactionResponse.model_validate(transaction)


@router.get(
    "/transactions",
    response_model=list[TransactionResponse],
    summary="List all transactions",
)
def get_transactions() -> list[TransactionResponse]:
    transactions = transaction_service.list_transactions()
    return [TransactionResponse.model_validate(item) for item in transactions]


@router.get(
    "/balance",
    response_model=BalanceResponse,
    summary="Get current balance",
)
def get_balance() -> BalanceResponse:
    balance, count = transaction_service.get_balance()
    return BalanceResponse(balance=balance, transaction_count=count)
