from fastapi import APIRouter, HTTPException, status

from app.database import get_transaction_by_id, insert_transaction, list_transactions
from app.schemas import TransactionAccepted, TransactionCreate, TransactionResponse

router = APIRouter(tags=["transactions"])


@router.post(
    "/transactions",
    response_model=TransactionAccepted,
    status_code=status.HTTP_201_CREATED,
)
def create_transaction(payload: TransactionCreate) -> TransactionAccepted:
    existing = get_transaction_by_id(payload.transaction_id)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="transaction_id already exists",
        )

    insert_transaction(payload.transaction_id, payload.amount)
    return TransactionAccepted(transaction_id=payload.transaction_id)


@router.get("/transactions", response_model=list[TransactionResponse])
def get_transactions() -> list[TransactionResponse]:
    rows = list_transactions()
    return [TransactionResponse.from_row(row) for row in rows]
