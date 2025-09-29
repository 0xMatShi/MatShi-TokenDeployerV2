import os
import base58
from solders.keypair import Keypair
from sqlalchemy import select
from database.engine import SessionFactory
from database.models import DevWallet
from loguru import logger
from interface.output import show_menu
from interface.constants import SELECT_MESSAGES


async def dev_choice_menu() -> Keypair | None:
    async with SessionFactory() as session:
        result = await session.execute(select(DevWallet))
        wallets = result.scalars().all()

    if not wallets:
        logger.warning("There are no Dev-Wallets in data-base")
        return None
    
    choices = [f"{w.name} ({w.public_key})" for w in wallets]

    choice = await show_menu(
        message=SELECT_MESSAGES[0],
        choices=choices
    )

    wallet = wallets[choices.index(choice)]

    kp = Keypair.from_bytes(base58.b58decode(wallet.private_key))
    logger.info(f"Selected Dev-Wallet: {wallet.public_key}")
    return kp