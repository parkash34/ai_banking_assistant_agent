import os
import requests
import json
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv


load_dotenv()

api_key = os.getenv("API_KEY")
if not api_key:
    raise ValueError("API Key is missing in .env file")

app = FastAPI()
memory = {}

class Message(BaseModel):
    session_id : str
    message : str

def system_prompt():
    return f"""
    You are PK, a banking assistant for SecureBank.
    Your goal is to help customers check balance, transfer money, and
    view transaction history.
    Always be professional, secure and trustworthy.
    Never reveal account details without verifications.
    Keep responses clear and concise.
    Always verify identity before any booking action.
    Never perform any transaction without successful verification.
    Never reveal another customer's information.
    Only answer banking related questions.

    Always respond in JSON format:
    {{
        "category" : "check balance, transfer money, transaction history or other",
        "status" : "success or error",
        "message" : "your response here",
        "data" : "any relevant data or null"
    }}

    Examples:

    User = How much money is available in my account?
    {{
        "category" : "check balance",
        "status" : "success",
        "message" : "Your current balance is 2298.00 euros.",
        "data" : 2298.00 euros
    }}

    User = How can I transfer money from this account to my new account?
    {{
        "category" : "transfer money",
        "status" : "success",
        "message" : "I can help you transfer money. Please provide your account number and PIN 
        for verification first.",
        "data" : null
    }}

    user = Can I see my last transaction history?
    {{
        "category" : "transaction history",
        "status" : "success",
        "message" : "Yes, I can show that but I will need verification.",
        "data" : null
    }}

    user = Who is president of USA?
    {{
        "category" : "other",
        "status" : "error",
        "message" : "I cannot help you with this matter, I can only answer questions related to
        our bank and if you have any, let me know",
        "data" : null
    }}
    
    """


database = {
    "ACC001": {
        "name": "Ahmed Khan",
        "pin": "1234",
        "balance": 5000.00,
        "transactions": [
            {"type": "credit", "amount": 1000, "description": "Salary", "date": "2024-03-01"},
            {"type": "debit", "amount": 500, "description": "Rent", "date": "2024-03-05"},
            {"type": "debit", "amount": 200, "description": "Groceries", "date": "2024-03-10"}
        ]
    },
    "ACC002": {
        "name": "Sara Ali",
        "pin": "5678",
        "balance": 3000.00,
        "transactions": [
            {"type": "credit", "amount": 2000, "description": "Freelance", "date": "2024-03-02"},
            {"type": "debit", "amount": 300, "description": "Bills", "date": "2024-03-08"}
        ]
    }
}

tools = [
    {
        "type": "function",
        "function": {
            "name": "verify_account",
            "description": "Verifies customer identity using account number and PIN before any banking action",
            "parameters": {
                "type": "object",
                "properties": {
                    "account_number": {
                        "type": "string",
                        "description": "Customer account number e.g. ACC001"
                    },
                    "pin": {
                        "type": "string",
                        "description": "4 digit PIN number"
                    }
                },
                "required": ["account_number", "pin"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "check_balance",
            "description": "Shows current balance of customer if it's account exists in bank account",
            "parameters": {
                "type": "object",
                "properties": {
                    "account_number": {
                        "type": "string",
                        "description": "Customer account number e.g. ACC001"
                    }
                },
                "required": ["account_number"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "transfer_money",
            "description": "Transfers money from one account to other account. Before transferring money it verifies both accounts and checks balance.",
            "parameters": {
                "type": "object",
                "properties": {
                    "from_account": {
                        "type": "string",
                        "description": "Customer account number e.g. ACC001"
                    },
                    "to_account": {
                        "type": "string",
                        "description": "Customer account number e.g. ACC001"
                    },
                    "amount": {
                        "type": "integer",
                        "description": "amount like e.g. 434"
                    }
                },
                "required": ["from_account", "to_account","amount"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "view_transactions",
            "description": "Shows last 5 transactions and before showing them, it verifies customer identity using account number",
            "parameters": {
                "type": "object",
                "properties": {
                    "account_number": {
                        "type": "string",
                        "description": "Customer account number e.g. ACC001"
                    }
                },
                "required": ["account_number"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_account_info",
            "description": "Showing information of account. before showing it verifies customer identity using account number",
            "parameters": {
                "type": "object",
                "properties": {
                    "account_number": {
                        "type": "string",
                        "description": "Customer account number e.g. ACC001"
                    }
                },
                "required": ["account_number"]
            }
        }
    }
]


def verify_account(account_number, pin):
    if account_number not in database:
        return "Account doesn't exist"
    if database[account_number]["pin"] != pin:
        return "Incorrect PIN"
    return "Verification successful."

def check_balance(account_number):
    if account_number not in database:
        return "Account doesn't exist"
    balance = database[account_number]["balance"]
    return f"Your current balance is : ${balance:.2f}\n"

def transfer_money(from_account, to_account, amount):
    if to_account not in database or from_account not in database:
        return "One or both account do not exist"
    if from_account == to_account:
        return "Cannot transfer to same account."
    amount = float(amount)
    if amount < 1:
        return "Minimum transfer amount is $1."
    if amount > 10_000:
        return "Maximum transfer amount is $10,000."
    if amount > database[from_account]["balance"]:
        return "Insufficient balance for this transfer."
    
    database[to_account]["balance"] += amount
    database[from_account]["balance"] -= amount
    return f"${amount:.2f} has been transfered {to_account} successfully"

def view_transactions(account_number):
    if account_number not in database:
        return "Account doesn't exist"
    transactions = database[account_number]["transactions"]
    result = "Your last transactions: \n"
    for i, t in enumerate(transactions[-5:],1):
        result += f"{i}. {t['date']} - {t['type'].upper()} ${t['amount']} - {t['description']}\n"
    return result

def get_account_info(account_number):
    if account_number not in database:
        return "Account doesn't exist"
    return f"""Name : {database[account_number]["name"]}\n
               Balance : ${database[account_number]["balance"]:.2f}"""


def ask_ai(chat_history):
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json = {
                "model": "llama-3.3-70b-versatile",
                "temperature" : 0.3,
                "max_tokens" : 500,
                "messages" : [
                    {"role" : "system", "content" : system_prompt()},
                    *chat_history
                ],
                "tools" : tools,
                "tool_choice" : "auto"
            },
            timeout=10
        )

        response.raise_for_status()
        message = response.json()["choices"][0]["message"]

        if message.get("tool_calls"):
            tool_call = message["tool_calls"][0]
            function_name = tool_call["function"]["name"]
            arguments = json.loads(tool_call["function"]["arguments"])


            if function_name == "verify_account":
                result = verify_account(**arguments)
            elif function_name == "check_balance":
                result = check_balance(**arguments)
            elif function_name == "transfer_money":
                arguments["amount"] = int(arguments["amount"])
                result = transfer_money(**arguments)
            elif function_name == "view_transactions":
                result = view_transactions(**arguments)
            elif function_name == "get_account_info":
                result = get_account_info(**arguments)
            else:
                result = "Function not found"

            chat_history.append(message)
            chat_history.append({
                "role" : "tool",
                "tool_call_id" : tool_call["id"],
                "content": result
            })


            final_response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json = {
                    "model": "llama-3.3-70b-versatile",
                    "temperature" : 0.3,
                    "max_tokens" : 500,
                    "messages" : [
                        {"role" : "system", "content" : system_prompt()},
                        *chat_history
                    ],
                    "tools" : tools,
                    "tool_choice" : "auto"
                },
                timeout=10
            )
            final_response.raise_for_status()
            raw = final_response.json()["choices"][0]["message"]["content"]
            return {"reply" : json.loads(raw)}
        content = message["content"]
        try:
            return {"reply" : json.loads(content)}
        except json.JSONDecodeError:
            return {"reply" : content}
    except requests.exceptions.Timeout:
        return "Time out! Please try again."
    except requests.exceptions.ConnectionError:
        return "Connection Error! Please check your network."
    except requests.exceptions.HTTPError as e:
        return f"API Error {e.response.status_code}"
    except Exception as e:
        return f"Something went wrong! {str(e)}"
    

@app.post("/bank")
def bank_chat(message : Message):
    if not message.session_id:
        return "Session ID is missing"
    if not message.message:
        return "Please type something before sending it."
    
    session_id = message.session_id
    user_message = message.message

    if session_id not in memory:
        memory[session_id] = []
    
    memory[session_id].append({"role" : "user", "content" : user_message})
    ai_reply = ask_ai(memory[session_id])

    if isinstance(ai_reply, dict) and "reply" in ai_reply:
        memory[session_id].append({"role" : "assistant", "content" : json.dumps(ai_reply["reply"])})

    return ai_reply
    

