import asyncio
import os
from loguru import logger
from aiohttp import ClientSession
from dotenv import load_dotenv

load_dotenv()

GOPLUS_URL = "https://api.gopluslabs.io/api/v1/token_security/1?contract_addresses="


async def get_goplus_api(session: ClientSession, token_address: str) -> dict:
    try:
        print
        response = await session.get(GOPLUS_URL + token_address)
        response.raise_for_status()
        return await response.json()
    except Exception as exc:
        # Handle other exceptions here
        logger.error(f"Goplus error occurred at {token_address}: {exc}")
