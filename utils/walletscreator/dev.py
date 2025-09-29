from solders.keypair import Keypair
from loguru import logger
from database.engine import SessionFactory
from database.models import DevWallet


# --- Для сохранения в БД ---
async def save_wallet(name: str, pubkey: str, privkey: str):
    """Сохраняем кошелёк в базу"""
    async with SessionFactory() as session:
        wallet = DevWallet(name=name, public_key=pubkey, private_key=privkey)
        session.add(wallet)
        await session.commit()

# --- Функция создания кошельков ---
async def create_dev_wallet():
    dev = input("Enter a name for the wallet (Press Enter if you change your mind): ").strip()
    if not dev:
        logger.warning("Creation canceled")
        return
    
    # Генерация пары ключей
    signer_keypair = Keypair()
    pubkey = str(signer_keypair.pubkey())
    privkey = str(signer_keypair)  # base58 строка

    await save_wallet(dev, pubkey, privkey)
    logger.info(f"Dev-Wallet has been created '{dev}' ({pubkey})")

