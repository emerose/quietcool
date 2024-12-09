import asyncio
import logging
import json
import argparse
from typing import Optional

from quietcool.client import Client
from quietcool.api import DataclassJSONEncoder

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
    parser = argparse.ArgumentParser(
        description='Quietcool Client\n\n'
                    'Connects to a QuietCool Wireless RF Control Kit via BLE\n\n'
                    'Commands:\n'
                    '  info: Dumps detailed information about the connected fan\n'
                    '  pair: Pairs the client with a fan (fan must be in pairing mode)\n\n'
                    'API ID:\n'
                    '  An API ID is required to connect to the fan. \n'
                    '  If no --id is provided, the API ID will be sourced in this order:\n'
                    '    1. QUIETCOOL environment variable\n'
                    '    2. /etc/quietcool file\n'
                    '    3. ~/.quietcool file\n'
                    '    4. ./.quietcool file\n\n'
                    'PAIRING:\n'
                    '  The API ID must be paired with the fan. In order to pair the API ID\n'
                    '  with the fan, set the fan to pairing mode on another device or push the\n'
                    '  "Pair" button on the controller. Then run the client with the pair command.\n\n',
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('command', nargs='?', default='info',
                        help='Command to execute (info or pair)')
    parser.add_argument('--id',
                        help='API ID string (see description for details)',
                        default=None)
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='WARNING',
        help='Set the logging level (default: WARNING)'
    )
    args = parser.parse_args()

    # Configure logging with user-specified level
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    asyncio.run(main(args.command, args.id))
