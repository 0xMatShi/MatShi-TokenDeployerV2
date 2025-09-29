import os
from dotenv import load_dotenv


load_dotenv()

RPC_URL = os.getenv("RPC_URL")

async def get_balance(session, pubkey: str) -> float:
    """Асинхронный запрос баланса через Solana RPC"""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getBalance",
        "params": [pubkey]
    }
    try:
        async with session.post(RPC_URL, json=payload) as resp:
            data = await resp.json()
            lamports = data.get("result", {}).get("value", 0)
            return lamports / 1_000_000_000
    except Exception as e:
        return f"Ошибка: {e}"
