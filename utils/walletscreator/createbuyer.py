from solders.keypair import Keypair
from loguru import logger
from database.engine import SessionFactory
from database.models import BuyerGroup, BuyerWallet
from sqlalchemy import select


async def create_buyer_group():
    async with SessionFactory() as session:
        # --- Название группы ---
        group_name = input(
            "Enter a name for the Buyer-Wallets Group (Enter if you have changed your mind): "
        ).strip()
        if not group_name:
            logger.warning("Creation cancelled")
            return

        # --- Проверяем, нет ли такой группы ---
        stmt = select(BuyerGroup).where(BuyerGroup.name == group_name)
        result = await session.execute(stmt)
        exists = result.scalar_one_or_none()
        if exists:
            logger.error(f"The group '{group_name}' already exists.")
            return

        # --- Сохраняем группу ---
        group = BuyerGroup(name=group_name)
        session.add(group)
        await session.flush()  # чтобы получить group.id без commit

        # --- Количество кошельков ---
        try:
            count = int(input("How many Buyer-Wallets should create? (default is 20): ") or 20)
        except ValueError:
            count = 20

        wallets = []
        for i in range(count):
            kp = Keypair()
            wallets.append(
                BuyerWallet(
                    group_id=group.id,
                    number=i + 1,
                    address=str(kp.pubkey()),
                    private_key=str(kp),
                )
            )

        session.add_all(wallets)
        await session.commit()

        logger.info(f"{count} Buyer-Wallets created in the '{group_name}' group.")
        for w in wallets:
            logger.info(f"{w.number}) {w.public_key}")


