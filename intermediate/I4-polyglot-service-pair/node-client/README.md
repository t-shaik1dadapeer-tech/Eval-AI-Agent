# Node.js Currency CLI Client

Calls the FastAPI `POST /convert` endpoint.

## Install

```bash
npm install
```

## Usage

```bash
node src/cli.js <amount> <from_currency> <to_currency>
```

**Example:**

```bash
node src/cli.js 100 USD INR
```

**Output:**

```
Converting 100 USD -> INR
Converted Amount: 8300
```

## Environment

```bash
export CONVERTER_API_URL=http://127.0.0.1:8000
```

## Error handling

| Scenario | Exit code | Message |
|----------|-----------|---------|
| Invalid CLI args | 1 | Usage + validation error |
| API validation/business error | 1 | `Error: <detail>` |
| Service unavailable | 2 | `Error: Currency conversion service is unavailable` |

## Test

```bash
npm test
```
