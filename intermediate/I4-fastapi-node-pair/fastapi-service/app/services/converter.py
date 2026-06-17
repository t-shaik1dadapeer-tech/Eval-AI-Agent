from __future__ import annotations

from typing import Dict, Tuple

SUPPORTED_CURRENCIES = frozenset({"USD", "INR", "EUR"})

# Hardcoded conversion rates (from_currency -> to_currency)
CONVERSION_RATES: Dict[Tuple[str, str], float] = {
    ("USD", "INR"): 83.0,
    ("INR", "USD"): 0.012,
    ("USD", "EUR"): 0.92,
    ("EUR", "USD"): 1.08,
}


class UnsupportedCurrencyPairError(ValueError):
    """Raised when no hardcoded rate exists for the currency pair."""


class ConverterService:
    def convert(self, amount: float, from_currency: str, to_currency: str) -> float:
        from_code = from_currency.upper()
        to_code = to_currency.upper()

        if from_code not in SUPPORTED_CURRENCIES:
            raise ValueError(f"Unsupported from_currency: {from_currency}")
        if to_code not in SUPPORTED_CURRENCIES:
            raise ValueError(f"Unsupported to_currency: {to_currency}")

        if from_code == to_code:
            return amount

        rate = CONVERSION_RATES.get((from_code, to_code))
        if rate is None:
            raise UnsupportedCurrencyPairError(
                f"No conversion rate defined for {from_code} -> {to_code}"
            )

        return round(amount * rate, 4)


converter_service = ConverterService()
