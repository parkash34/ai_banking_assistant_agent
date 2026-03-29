# SecureBank — AI Banking Assistant Agent

An AI-powered banking assistant built with FastAPI and Groq AI.
The agent handles real banking actions through natural conversation
with full identity verification before any financial transaction.

## Features

- Identity verification — PIN and account number validation before any action
- Balance checking — real-time account balance retrieval
- Money transfers — with full validation and transfer limits
- Transaction history — last 5 transactions displayed clearly
- Account information — secure account details retrieval
- Structured JSON responses — consistent format for all replies
- Multi-session memory — each customer has a separate conversation history
- Comprehensive error handling — wrong PIN, insufficient balance, invalid accounts

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| FastAPI | Backend web framework |
| Groq API | AI language model provider |
| LLaMA 3.3 70B | AI model |
| Pydantic | Data validation |
| python-dotenv | Environment variable management |

## Project Structure
```
securebank-agent/
│
├── .venv/               
├── main.py            
├── .env               
└── requirements.txt   
```

## Setup

1. Clone the repository
```
git clone https://github.com/yourusername/securebank-agent
```

2. Create and activate a virtual environment
```
python -m venv .venv
.venv\Scripts\activate
```

3. Install dependencies
```
pip install -r requirements.txt
```

4. Create a `.env` file and add your Groq API key
```
API_KEY=your_groq_api_key_here
```

5. Run the server
```
uvicorn main:app --reload
```

## API Endpoint

### POST /bank

**Request:**
```json
{
    "session_id": "user_1",
    "message": "What is my current balance?"
}
```

**Response:**
```json
{
    "reply": {
        "category": "check balance",
        "status": "success",
        "message": "Your current balance is $5000.00",
        "data": 5000.0
    }
}
```

## Available Banking Tools

| Tool | Description | Requires Verification |
|---|---|---|
| `verify_account` | Validates account number and PIN | No |
| `check_balance` | Returns current balance | Yes |
| `transfer_money` | Transfers funds between accounts | Yes |
| `view_transactions` | Shows last 5 transactions | Yes |
| `get_account_info` | Returns account details | Yes |

## Security Rules

- Identity must be verified before any banking action
- PIN is never exposed in any response
- Customer information is never shared across sessions
- Only banking-related questions are answered

## Transfer Limits

- Minimum transfer: $1
- Maximum transfer: $10,000
- Cannot transfer to the same account

## Test Accounts
```
Account: ACC001 | PIN: 1234 | Balance: $5000.00
Account: ACC002 | PIN: 5678 | Balance: $3000.00
```

## How It Works
```
Customer sends a message
↓
AI decides which banking tool to call
↓
Identity verified before any action
↓
Python executes the banking function
↓
Result sent back to AI with tool role
↓
AI generates a natural, friendly response
↓
Customer receives structured JSON reply
```

## Environment Variables
```
API_KEY=your_groq_api_key_here
```

## Notes

- Never commit your .env file to GitHub
- Test accounts are hardcoded — no real database

## 👤 Author

**Ohm Parkash** — [LinkedIn](https://www.linkedin.com/in/om-parkash34/) · [GitHub](https://github.com/parkash34)
