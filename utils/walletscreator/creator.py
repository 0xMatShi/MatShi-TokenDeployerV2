import os
from utils.walletscreator.dev import create_dev_wallet
from utils.walletscreator.buyer import create_buyer_group
from interface.output import show_menu
from interface.constants import MESSAGES, CREATOR_CHOICES


def clear_console():
    os.system("cls" if os.name == "nt" else "clear")


async def wallets_creator():
    choice = await show_menu(
        message=MESSAGES[2], 
        choices=CREATOR_CHOICES
    )

    if choice == "Dev-Wallet Creation":
        clear_console()
        await create_dev_wallet()
    elif choice == "Buyer-Wallets Group Creation":
        clear_console()
        await create_buyer_group()
    else:
        return