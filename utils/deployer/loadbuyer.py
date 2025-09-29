import base58
from solders.keypair import Keypair
from InquirerPy import inquirer
from sqlalchemy import select
from database.engine import SessionFactory
from database.models import BuyerGroup, BuyerWallet
from loguru import logger
from interface.output import show_menu
from interface.constants import SELECT_MESSAGES


async def buyer_group_choice_menu() -> int | None:
    async with SessionFactory() as session:
        result = await session.execute(select(BuyerGroup))
        groups = result.scalars().all()

    if not groups:
        logger.warning("There are no Buyer-Wallets Groups.")
        return None

    choices = [f"{g.name} (ID: {g.id})" for g in groups]
    choice = await show_menu(
        message=SELECT_MESSAGES[1],
        choices=choices,
    )

    group = groups[choices.index(choice)]
    logger.info(f"Selected Buyer-Wallets Group: {group.name} (ID: {group.id})")
    wallets = await load_buyer_wallets(group.id)
    return wallets


async def load_buyer_wallets(group_id: int) -> list[dict]:
    wallets: list[dict] = []

    async with SessionFactory() as session:
        result = await session.execute(
            select(BuyerWallet).where(BuyerWallet.group_id == group_id)
        )
        rows = result.scalars().all()

    for w in rows:
        try:
            raw = base58.b58decode(w.private_key)
            kp = Keypair.from_bytes(raw)
            wallets.append({"address": str(kp.pubkey()), "keypair": kp})
        except Exception as e:
            logger.error(f"Error while loading wallet {w.address}: {e}")

    return wallets
