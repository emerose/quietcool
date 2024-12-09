import asyncio
import logging

from quietclient.client import Client

# Add logger configuration at the top
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


CORRECT_PAIR_ID = "aa4a737ffd756c6d"
INCORRECT_PAIR_ID = "a1b2c1d2a2b1c2d1"


async def main() -> None:
    client = await Client.create(INCORRECT_PAIR_ID)

   #    print(await client.api.testcmd())
    await client.doit()


if __name__ == "__main__":
    asyncio.run(main())
