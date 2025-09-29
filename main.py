import urllib3
import os
import logging
import sys
import asyncio
from loguru import logger
from process import start


def clear_console():
    os.system("cls" if os.name == "nt" else "clear")


async def main():
    clear_console()

    configuration()
    await start()


log_format = (
    "<light-blue>[</light-blue><yellow>{time:HH:mm:ss}</yellow><light-blue>]</light-blue> | "
    "<level>{level: <8}</level> | "
    "<cyan>{file}:{line}</cyan> | "
    "<level>{message}</level>"
)


def configuration():
    urllib3.disable_warnings()
    logger.remove()

    # Disable primp, sqlalchemy and web3 logging
    logging.getLogger("primp").setLevel(logging.WARNING)
    logging.getLogger("web3").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    logger.add(
        sys.stdout,
        colorize=True,
        format=log_format,
    )
    logger.add(
        "logs/app.log",
        rotation="10 MB",
        retention="1 month",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{line} - {message}",
        level="INFO",
    )


if __name__ == "__main__":
    asyncio.run(main())