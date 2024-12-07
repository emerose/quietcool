import asyncio
import json
import logging
from io import StringIO
from itertools import count, takewhile
from typing import Iterator, Optional, Any

from bleak import BleakClient, BleakScanner
from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.backends.device import BLEDevice

from lib.api import Api
from lib.device import Device

# Add logger configuration at the top
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

ATTIC_FAN = "71604280-3C9B-1EE6-9378-E5CC8402DB49"


PAIR_ID = "aa4a737ffd756c6d"
# PAIR_ID = "a1b2c1d2a2b1c2d1"


async def do_it() -> None:
    try:
        device = await Device.find_fan()
        api = Api(device)
        await api.login(PAIR_ID)

        await api.get_parameter()

        await asyncio.sleep(120)
    except asyncio.exceptions.CancelledError:
        # task is cancelled on disconnect, so we ignore this error
        pass
    except Exception as e:
        logger.error("Error occurred: %s", str(e))


if __name__ == "__main__":
    asyncio.run(do_it())
