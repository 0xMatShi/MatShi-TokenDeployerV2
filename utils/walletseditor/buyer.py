import os
from loguru import logger
from database.engine import SessionFactory
from database.models import BuyerGroup, BuyerWallet
from sqlalchemy import select, delete, update
from interface.output import show_menu
from interface.constants import SELECT_MESSAGES, ACTION, ACTION_BUYER_CHOICES, ACTION_BUYER_WALLET


def clear_console():
    os.system("cls" if os.name == "nt" else "clear")


async def select_buyer_group(session):
    result = await session.execute(select(BuyerGroup))
    groups = result.scalars().all()

    if not groups:
        logger.warning("There are no Buyer-Wallets Groups.")
        input("\nPress Enter to continue...")
        return None

    choices = [f"{g.name} (ID: {g.id})" for g in groups]
    choice = await show_menu(
        message=SELECT_MESSAGES[1], 
        choices=choices
    )
    return groups[choices.index(choice)]


async def edit_buyer_group():
    async with SessionFactory() as session:
        group = await select_buyer_group(session)
        if not group:
            return

        while True:
            clear_console()
            print(f"\n[+] Группа: {group.name}\n")

            choice = await show_menu(
                message=ACTION,
                choices=ACTION_BUYER_CHOICES
            )

            if choice == "Edit Name":
                new_name = input("Enter a new name: ").strip()
                if new_name:
                    await session.execute(
                        update(BuyerGroup).where(BuyerGroup.id == group.id).values(name=new_name)
                    )
                    await session.commit()
                    group.name = new_name
                    logger.info("Name of this group has been changed")
                    input("\nPress enter to continue...")

            elif choice == "Delete This Group":
                confirm = input(f"Delete this group '{group.name}'? (y/n): ").strip().lower()
                if confirm == "y":
                    # удаляем кошельки этой группы
                    await session.execute(delete(BuyerWallet).where(BuyerWallet.group_id == group.id))
                    await session.execute(delete(BuyerGroup).where(BuyerGroup.id == group.id))
                    await session.commit()
                    logger.warning(f"Group'{group.name}' has been deleted")
                    input("\nPress Enter to continue...")
                    return

            elif choice == "View Buyer-Wallets":
                await edit_buyer_wallets(session, group.id, group.name)

            else:
                return


async def edit_buyer_wallets(session, group_id: int, group_name: str):
    result = await session.execute(select(BuyerWallet).where(BuyerWallet.group_id == group_id))
    wallets = result.scalars().all()

    if not wallets:
        logger.warning("There are no wallets in this group.")
        input("\nPress Enter to continue...")
        return

    choices = [f"{w.number} ({w.address})" for w in wallets]
    choice = await show_menu(
        message=SELECT_MESSAGES[2],
        choices=choices,
    )

    wallet = wallets[choices.index(choice)]

    while True:
        clear_console()
        print(f"\nBuyer Wallet {wallet.number}:\n")
        print(f"Public Key: {wallet.address}")
        print(f"Private Key: {wallet.private_key}")

        action = await show_menu(
            message=ACTION,
            choices=ACTION_BUYER_WALLET
        )

        if action == "Delete This Wallet":
            confirm = input("Delete this wallet? (y/n): ").strip().lower()
            if confirm == "y":
                await session.execute(delete(BuyerWallet).where(BuyerWallet.id == wallet.id))
                await session.commit()
                logger.warning("Buyer-wallet has been deleted")
                input("\nPress Enter to continue...")
                return
        else:
            return
