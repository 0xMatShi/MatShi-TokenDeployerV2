from tabulate import tabulate
from InquirerPy import inquirer
from loguru import logger
import aiohttp
import asyncio
from sqlalchemy import select
from database.engine import SessionFactory
from database.models import BuyerGroup, BuyerWallet
from utils.balancechecker.getbalance import get_balance
from interface.output import show_menu
from interface.constants import SELECT_MESSAGES


async def check_buyer_wallets():
    async with SessionFactory() as session:
        result = await session.execute(select(BuyerGroup))
        groups = result.scalars().all()

    if not groups:
        logger.warning("There are no Buyer-Wallets Groups in the database.")
        input("\nPress Enter to continue...")
        return

    choices = [f"{g.name} (ID: {g.id})" for g in groups]
    choice = await show_menu(
        message=SELECT_MESSAGES[1], 
        choices=choices
    )
    group = groups[choices.index(choice)]

    async with SessionFactory() as session:
        result = await session.execute(
            select(BuyerWallet).where(BuyerWallet.group_id == group.id)
        )
        wallets = result.scalars().all()

    if not wallets:
        logger.warning(f"In the group '{group.name}' there are no wallets.")
        input("\nPress Enter to continue...")
        return

    async with aiohttp.ClientSession() as http:
        balances = await asyncio.gather(
            *[get_balance(http, w.address) for w in wallets]
        )

    table = [[w.number, w.address, f"{b:.6f}"] for w, b in zip(wallets, balances)]
    logger.info(
        f"\n\nBalances of Buyer-Wallets (group '{group.name}'):\n"
        + tabulate(
            table, 
            headers=["№", "Address", "Balance (SOL)"], 
            tablefmt="pretty"
            )
        )
    input("\nPress Enter to continue...")