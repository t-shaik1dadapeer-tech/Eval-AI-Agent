from fastapi import APIRouter, HTTPException, status

from app.schemas.convert import ConvertRequest, ConvertResponse
from app.services.converter import UnsupportedCurrencyPairError, converter_service

router = APIRouter(tags=["convert"])


@router.post(
    "/convert",
    response_model=ConvertResponse,
    status_code=status.HTTP_200_OK,
    summary="Convert currency amount using hardcoded rates",
)
def convert_currency(payload: ConvertRequest) -> ConvertResponse:
    try:
        converted = converter_service.convert(
            payload.amount, payload.from_currency, payload.to_currency
        )
    except UnsupportedCurrencyPairError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return ConvertResponse(
        amount=payload.amount,
        from_currency=payload.from_currency,
        to_currency=payload.to_currency,
        converted_amount=converted,
    )
