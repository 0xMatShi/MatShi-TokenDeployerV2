import os
from loguru import logger
from database.engine import SessionFactory
from database.models import DevWallet
from sqlalchemy import select, delete, update
from interface.output import show_menu
from interface.constants import SELECT_MESSAGES, ACTION, ACTION_DEV_CHOICES

def clear_console():
    os.system("cls" if os.name == "nt" else "clear")


async def select_dev_wallet(session):
    """Асинхронный выбор dev-кошелька"""
    model = DevWallet
    result = await session.execute(select(model))
    wallets = result.scalars().all()

    if not wallets:
        logger.warning("There are no Dev-Wallets in the database.")
        input("\nPress Enter ot continue...")
        return None

    choices = [f"{w.name} ({w.public_key})" for w in wallets]
    choice = await show_menu(
        message=SELECT_MESSAGES[0], 
        choices=choices
    )
    return wallets[choices.index(choice)], model


async def edit_dev_wallet():
    async with SessionFactory() as session:
        wallet, model = await select_dev_wallet(session)
        if not wallet:
            return

        while True:
            clear_console()
            print(f"\nDev-Wallet '{wallet.name}':\n")
            print(f"Public Key: {wallet.public_key}")
            print(f"Private Key: {wallet.private_key}")

            choice = await show_menu(
                message=ACTION,
                choices=ACTION_DEV_CHOICES
            )

            if choice == "Edit Name":
                new_name = input("Enter a new name: ").strip()
                if new_name:
                    await session.execute(
                        update(model).where(model.id == wallet.id).values(name=new_name)
                    )
                    await session.commit()
                    wallet.name = new_name
                    logger.info("Name has been changed")
                    input("\nPress Enter to continue...")

            elif choice == "Delete This Wallet":
                confirm = input("Delete this wallet? (y/n): ").strip().lower()
                if confirm == "y":
                    await session.execute(delete(model).where(model.id == wallet.id))
                    await session.commit()
                    logger.warning("Wallet has been deleted")
                    input("\nPress Enter to Continue...")
                    return

            else:
                return
