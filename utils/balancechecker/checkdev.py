from loguru import logger
import aiohttp
from sqlalchemy import select
from database.engine import SessionFactory
from database.models import DevWallet
from utils.balancechecker.getbalance import get_balance
from interface.output import show_menu
from interface.constants import SELECT_MESSAGES


async def check_dev_wallets():
    async with SessionFactory() as session:
        result = await session.execute(select(DevWallet))
        wallets = result.scalars().all()

    if not wallets:
        logger.warning("There are no Dev-Wallets in the database.")
        input("\nPress Enter to continue...")
        return

    choices = [f"{w.name} ({w.public_key})" for w in wallets]
    choice = await show_menu(
        message=SELECT_MESSAGES[0], 
        choices=choices
    )
    wallet = wallets[choices.index(choice)]

    async with aiohttp.ClientSession() as http:
        balance = await get_balance(http, wallet.public_key)

    logger.info(f"\nБаланс '{wallet.name}' ({wallet.public_key}): {balance:.6f} SOL")
    input("\nPress Enter to continue...")