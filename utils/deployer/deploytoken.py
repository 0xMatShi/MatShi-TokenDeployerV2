import os
from loguru import logger
from interface.output import show_menu
from interface.constants import ACTION, DEPLOYER_ACTION, PLATFORM_CHOICE, SELECT_MESSAGES
from utils.deployer.deploytx import deploy_pump_tx
from utils.deployer.trade import start_trade

def clear_console():
    os.system("cls" if os.name == "nt" else "clear")


async def deploy_token():
    clear_console()

    choice = await show_menu(
        message=ACTION,
        choices=DEPLOYER_ACTION
    )

    if choice == "Create Token":
        portal_choice = await platform_choice()
        if portal_choice == "Pump.Fun":
            buyer_group, dev_wallet, mint_keypair = await deploy_pump_tx()
            await start_trade(buyer_group, dev_wallet, mint_keypair)
            input("\nPress Enter to continue")
    else:
        return
    
    



async def platform_choice():
    clear_console()
    logger.info("На какой площадке хотите создать токен?")
    portal_choice = await show_menu(
        message=SELECT_MESSAGES[3],
        choices=PLATFORM_CHOICE,
    )
    
    if portal_choice == "Pump.Fun":
        logger.info(f"\nSelected platform: {portal_choice}")
        return portal_choice
        
    elif portal_choice == "Bonk.Fun":
        logger.info(f"\n{portal_choice} isn't available now")
        input("\nPress Enter to continue...")
        return