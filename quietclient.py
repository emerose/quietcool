import asyncio
import logging
import argparse
from typing import Optional

from quietclient.client import Client

# Add logger configuration at the top
logger = logging.getLogger(__name__)


async def main(api_id: Optional[str] = None) -> None:
    client = await Client.create(api_id=api_id)

    await client.doit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Quiet Client')
    parser.add_argument('--id', help='API ID string', default=None)
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='INFO',
        help='Set the logging level'
    )
    args = parser.parse_args()

    # Configure logging with user-specified level
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    asyncio.run(main(args.id))
