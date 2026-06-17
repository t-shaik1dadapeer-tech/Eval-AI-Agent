from fastapi import APIRouter, status

from app.schemas.transaction import TransactionAccepted, TransactionCreate
from app.services.queue_service import enqueue_transaction

router = APIRouter(tags=["transactions"])


@router.post(
    "/transactions",
    response_model=TransactionAccepted,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Ingest a transaction into the file queue",
)
def create_transaction(payload: TransactionCreate) -> TransactionAccepted:
    enqueue_transaction(payload)
    return TransactionAccepted(transaction_id=payload.transaction_id)
