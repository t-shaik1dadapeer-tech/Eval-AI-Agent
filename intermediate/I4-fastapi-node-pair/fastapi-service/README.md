# FastAPI Currency Converter

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload --port 8000
```

Docs: `http://127.0.0.1:8000/docs`

## Endpoint

### POST /convert

**Request:**

```json
{
  "amount": 100,
  "from_currency": "USD",
  "to_currency": "INR"
}
```

**Response (200):**

```json
{
  "amount": 100,
  "from_currency": "USD",
  "to_currency": "INR",
  "converted_amount": 8300
}
```

## Validation

- `amount` > 0 (422 if invalid)
- `from_currency` / `to_currency` must be `USD`, `INR`, or `EUR` (422)
- Pair must have a hardcoded rate (400 if unsupported)

## Test

```bash
pytest -v
```
