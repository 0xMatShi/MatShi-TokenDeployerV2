import os
import asyncio
import aiohttp
import base58
import random
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solders.commitment_config import CommitmentLevel
from solders.rpc.requests import SendVersionedTransaction
from solders.rpc.config import RpcSendTransactionConfig
from dotenv import load_dotenv
from loguru import logger
from utils.deployer.swaptx import (
    get_quote, 
    get_swap_tx, 
    sign_and_send_swap,
    get_token_balance,
    get_sol_balance
)


load_dotenv()
SOL_MINT = os.getenv("SOL_MINT")

async def jupiter_swap(wallet: Keypair, mint: str, action: str):
    async with aiohttp.ClientSession() as session:
        if action == "buy":
            sol_balance = await get_sol_balance(session, wallet)
            safe_balance = int(sol_balance * 0.95)
            pct = 0.1
            lamports = int(safe_balance * pct)
            amount_sol = lamports / 1_000_000_000
            input_mint = SOL_MINT
            output_mint = mint
            logger.info(f"[{wallet.pubkey()}] BUY {mint} of {amount_sol:.4f} SOL")
        else:
            balance = await get_token_balance(session, wallet, mint)
            lamports = balance
            input_mint = mint
            output_mint = SOL_MINT
            logger.info(f"[{wallet.pubkey()}] SELL 100% {mint}")

        # 1) получаем котировку
        quote = await get_quote(session, input_mint, output_mint, lamports)

        # 2) получаем готовую транзакцию swap
        swap_tx = await get_swap_tx(session, quote, str(wallet.pubkey()))

        # 3) подписываем и шлём в Solana
        sig = await sign_and_send_swap(session, swap_tx, wallet)
        logger.info(f"[{wallet.pubkey()}] {action.upper()} tx: https://solscan.io/tx/{sig}")


async def mass_trade(wallets: list[Keypair], mint: str, action: str):
    await asyncio.gather(*[jupiter_swap(w, mint, action) for w in wallets])


async def start_trade(wallets: list[Keypair], dev_wallet: Keypair, mint: str):

    logger.info("\nMass buy via Jupiter...\n")
    await mass_trade(wallets, mint, "buy")
    logger.info("All wallets have bought a token")

    input("\nPress Enter sell on Dev-Wallet...")
    await jupiter_swap(dev_wallet, mint, "sell")
    
    input("\nPress Enter for mass sell via Jupiter...")
    await mass_trade(wallets, mint, "sell")
    logger.info("All wallets have sold a token")
