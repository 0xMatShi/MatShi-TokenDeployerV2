import os
from interface.output import show_menu
from interface.constants import MESSAGES, EDITOR_CHOICES
from utils.walletseditor.editdev import edit_dev_wallet
from utils.walletseditor.editbuyer import edit_buyer_group


def clear_console():
    os.system("cls" if os.name == "nt" else "clear")


async def wallets_editor():
    while True:
        clear_console()
        choice = await show_menu(
            message=MESSAGES[3], 
            choices=EDITOR_CHOICES
        )

        if choice == "Edit Dev-Wallet":
            clear_console()
            await edit_dev_wallet()
        elif choice == "Edit Buyer-Wallets Group":
            clear_console()
            await edit_buyer_group()
        else:
            return