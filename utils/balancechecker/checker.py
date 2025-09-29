import os
from interface.constants import MESSAGES, CHECKER_CHOICES
from interface.output import show_menu
from utils.balancechecker.dev import check_dev_wallets
from utils.balancechecker.buyer import check_buyer_wallets

def clear_console():
    os.system("cls" if os.name == "nt" else "clear")


async def balance_checker():
    while True:
        clear_console()  # убираем баннер при входе
        choice = await show_menu(
            message=MESSAGES[4], 
            choices=CHECKER_CHOICES
        )

        if choice == "Check Dev-Wallet":
            clear_console()
            await check_dev_wallets()
        elif choice == "Check Buyer-Wallets Group":
            clear_console()
            await check_buyer_wallets()
        else:
            return
        
