import asyncio
import os
from loguru import logger
from aiohttp import ClientSession
from dotenv import load_dotenv

load_dotenv()

TRANSPOSE_GET_URL = "https://api.transpose.io/endpoint"
TRANSPOSE_QUERY_URL = "https://api.transpose.io/sql"
TRANSPOSE_API_KEY = os.getenv("TRANSPOSE_API_KEY")

HEADERS = {
    'Content-Type': 'application/json',
    'X-API-KEY': TRANSPOSE_API_KEY,
}

async def get_transpose_api(session: ClientSession, endpoint: str, params: dict = {}) -> dict:
    try:
        print
        response = await session.get(TRANSPOSE_GET_URL + endpoint,
                                     headers=HEADERS,
                                     params=params
                                     )
        logger.info('Credits charged: {credits}', credits=response.headers.get('X-Credits-Charged', None))
        response.raise_for_status()
        return await response.json()
    except Exception as exc:
        # Handle other exceptions here
        logger.error(f"Transpose error occurred: {exc}")
