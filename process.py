import sys
import os
from interface.output import show_menu, show_logo
from interface.constants import MESSAGES, MAIN_MENU_CHOICES
from loguru import logger
from utils.walletscreator.creator import wallets_creator
from utils.balancechecker.checker import balance_checker
from utils.walletseditor.editor import wallets_editor
from utils.deployer.deploytoken import deploy_token

def clear_console():
    os.system("cls" if os.name == "nt" else "clear")



async def start():
    while True:
        show_logo()
        choice = await show_menu(
            message=MESSAGES[0], 
            choices=MAIN_MENU_CHOICES
        )

        if choice == "Start Deploy":
            clear_console()
            await deploy_token()
        elif choice == "Create Wallets":
            clear_console()
            await wallets_creator()
        elif choice == "Edit Wallets":
            clear_console()
            await wallets_editor()
        elif choice == "Check Balances":
            clear_console()
            await balance_checker()
        elif choice == "Exit":
            logger.info("Exiting the program...") 
            sys.exit(0)
        