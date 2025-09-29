import os
import aiohttp
import random 
import json
from utils.deployer.loaddev import dev_choice_menu
from utils.deployer.loadbuyer import buyer_group_choice_menu
from loguru import logger
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solders.rpc.config import RpcSendTransactionConfig
from solders.rpc.requests import SendVersionedTransaction
from solders.commitment_config import CommitmentLevel
from dotenv import load_dotenv


load_dotenv()
PUMP_URL = os.getenv("PUMP_URL")
RPC_URL = os.getenv("RPC_URL")


def clear_console():
    os.system("cls" if os.name == "nt" else "clear")


async def deploy_pump_tx():
    clear_console()
    dev_wallet = await dev_choice_menu()
    buyer_group = await buyer_group_choice_menu()

    if not dev_wallet or not buyer_group:
        logger.warning("There are no available wallets for deploy.")
        return
    
    mint_keypair = await generate_vanity_keypair("pump")

    form_data = await get_token_metadata()    

    async with aiohttp.ClientSession() as session:
        # 5. IPFS upload
        ipfs_url = "https://pump.fun/api/ipfs"
        form = aiohttp.FormData()
        for k, v in form_data.items():
            if k != "image_path":
                form.add_field(k, str(v))
        form.add_field(
            "file", 
            open(form_data['image_path', 'rb']),
            filename=os.path.basename(form_data["image_path"]),
            content_type="image/png"
        )

        async with session.post(ipfs_url, data=form) as resp:
            metadata_response_json = await resp.json()

        # 6. JSON для деплоя
        token_metadata = {
            "name": form_data["name"],
            "symbol": form_data["symbol"],
            "uri": metadata_response_json["metadataUri"],
        }

        amount_sol = max(0.001, round(random.uniform(0.001, 0.001), 6))

        deploy_payload = {
            "publicKey": str(dev_wallet.pubkey()),
            "action": "create",
            "tokenMetadata": token_metadata,
            "mint": str(mint_keypair.pubkey()),
            "denominatedInSol": "true",
            "amount": amount_sol,
            "slippage": 10,
            "priorityFee": 0.00001,
            "pool": "pump",
        }

        async with session.post(
            PUMP_URL,
            headers={"Content-Type": "application/json"},
            data=json.dumps(deploy_payload),
        ) as resp:
            raw_bytes = await resp.read()

    tx = VersionedTransaction(
        VersionedTransaction.from_bytes(raw_bytes).message,
        [mint_keypair, dev_wallet],
    )
    config = RpcSendTransactionConfig(preflight_commitment=CommitmentLevel.Confirmed)

    async with aiohttp.ClientSession() as session:
        async with session.post(
            RPC_URL,
            headers={"Content-Type": "application/json"},
            data=SendVersionedTransaction(tx, config).to_json(),
        ) as resp:
            rpc_response = await resp.json()

    tx_signature = rpc_response.get("result")
    logger.info(f"\n[+] Transaction: https://solscan.io/tx/{tx_signature}")
    logger.info(f"[+] Token CA: {mint_keypair.pubkey()}")

    return buyer_group, dev_wallet, mint_keypair

async def generate_vanity_keypair(platform: str):
    suffix = "pump" if platform.lower() == "pump" else "bonk"
    logger.info(f"Starting generating vanity-address with suffix '{suffix}'")

    attempt = 0
    while True:
        kp = Keypair()
        pubkey_str = str(kp.pubkey())
        attempt += 1
        if pubkey_str.endswith(suffix):
            logger.info(f"Found the vanity-address after {attempt} attempts: {pubkey_str}")
            return kp
        if attempt % 100000 == 0:
            logger.info(f"Attempts: {attempt}... No matches yet")


async def get_token_metadata():
    while True:
        logger.info("\Enter token metadata:\n")
        name = input("1) Name: ").strip()
        symbol = input("2) Ticker: ").strip()
        description = input("3) Discription: ").strip()
        twitter = input("4) Twitter ('-' if not): ").strip()
        telegram = input("5) Telegram ('-' if not): ").strip()
        website = input("6) Website ('-' if not): ").strip()

        while True:
            image_path = input("7) Path to image: ").strip()
            if image_path == "":
                image_path = "./images/example.png"
            if os.path.isfile(image_path):
                break
            else:
                logger.warning("The file was not found, please try again.")

        confirm = input(f"\Ready to create token {name}? (Yes(y)/No(n)): ").strip().lower()
        if confirm in ["yes", "y"]:
            return {
                'name': name,
                'symbol': symbol,
                'description': description,
                'twitter': "" if twitter == "" else twitter,
                'telegram': "" if telegram == "" else telegram,
                'website': "" if website == "" else website,
                'showName': 'true',
                'image_path': image_path
            }
        else:
            logger.info("\Specify the metadata again...\n")


