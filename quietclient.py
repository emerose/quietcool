import asyncio
import logging
import json
import argparse
from typing import Optional

from quietclient.client import Client
from quietclient.api import DataclassJSONEncoder

logger = logging.getLogger(__name__)

# this allows us to dump dataclasses to json easily
json.JSONEncoder = DataclassJSONEncoder


async def main(command: str, api_id: Optional[str] = None) -> None:
    client = await Client.create(api_id=api_id)

    match command.lower():
        case "info" | "":
            info = await client.get_info()
            print(json.dumps(info, indent=2))
        case "pair":
            await client.pair()
        case _:
            logger.error(f"Unknown command: {command}")
            raise ValueError(f"Unknown command: {command}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Quiet Client')
    parser.add_argument('command', nargs='?', default='info',
                        help='Command to execute (info, pair)')
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

    asyncio.run(main(args.command, args.id))
