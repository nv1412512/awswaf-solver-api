# AWS WAF Solver API

A lightweight FastAPI service that solves AWS WAF challenges and returns a valid `aws-waf-token`.

> This was my first time reverse engineering an antibot — some parts of the code may be a bit rough around the edges. Use at your own risk.

> **For research and educational purposes only.**

## Requirements

- Python 3.10+
- `rnet`
- `AWSSolver`
- `fastapi`
- `uvicorn`

## Installation

```bash
pip install fastapi uvicorn rnet
```

> Make sure `AWSSolver` is installed or present in your project directory.

## Start

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Usage

**POST** `/solve`

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `url` | string | ✅ | The URL to fetch the WAF challenge from |
| `user_agent` | string | ✅ | The User-Agent to use for the request |
| `domain` | string | ❌ | Domain override — auto-extracted from `url` if omitted |

### Example

```bash
curl -X POST http://localhost:8000/solve \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.binance.com/",
    "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"
  }'
```

### Response

```json
{
  "token": "your-aws-waf-token-here"
}
```

Use the token as a cookie on subsequent requests:

```
Cookie: aws-waf-token=your-aws-waf-token-here
```

## Domain Handling

The `domain` field is optional. If omitted, it is automatically extracted from the `url` and prefixed with `www.` if not already present.

| Input | Resolved Domain |
|---|---|
| `https://www.binance.com/en` | `www.binance.com` |
| `https://binance.com/` | `www.binance.com` |
| `binance.com` | `www.binance.com` |