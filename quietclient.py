import asyncio
import json
import logging
from io import StringIO
from itertools import count, takewhile
from typing import Iterator, Optional, Any

from bleak import BleakClient, BleakScanner
from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.backends.device import BLEDevice

# Add logger configuration at the top
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

ATTIC_FAN = "71604280-3C9B-1EE6-9378-E5CC8402DB49"

UUID_SERVER = "000000ff-0000-1000-8000-00805f9b34fb"
UUID_KEY_DATA = "0000ff01-0000-1000-8000-00805f9b34fb"
UUID_KEY_NOTIFY = "00002902-0000-1000-8000-00805f9b34fb"

PAIR_ID = "aa4a737ffd756c6d"
# PAIR_ID = "a1b2c1d2a2b1c2d1"


class Fan:
    def __init__(self) -> None:
        self.send_buffer: StringIO = StringIO()
        self.receive_buffer: StringIO = StringIO()
        self.fan: Optional[BLEDevice] = None
        self.connected: bool = False
        self.client: Optional[BleakClient] = None
        self.data_waiting: asyncio.Semaphore = asyncio.Semaphore(0)
        self.packet_counter: int = 0
        self.logged_in: bool = False

    def sliced(self, data: bytes, n: int) -> Iterator[bytes]:
        """
        Slices *data* into chunks of size *n*. The last slice may be smaller than
        *n*.
        """
        return takewhile(len, (data[i: i + n] for i in count(0, n)))

    async def find_fan(self) -> None:
        self.fan = await BleakScanner.find_device_by_filter(
            lambda d, ad: d.name and d.name.startswith("ATTICFAN"), timeout=3
        )
        if self.fan is None:
            raise Exception("No fan found")
        logger.info("Found fan: %s", self.fan.name)

    def handle_disconnect(self, _: BleakClient) -> None:
        logger.info("Device was disconnected, goodbye.")
        self.connected = False
        for task in asyncio.all_tasks():
            task.cancel()

    def handle_rx(self, _: BleakGATTCharacteristic, data: bytearray) -> None:
        logger.debug("received: %s", data)
        str = data.decode('utf-8')
        self.receive_buffer.write(str)
        self.data_waiting.release()

    async def get_response(self) -> dict:
        while True:
            await self.data_waiting.acquire()
            try:
                value = json.loads(self.receive_buffer.getvalue())
                logger.debug("Received response %s in %d packets",
                             value, self.packet_counter)
                self.packet_counter = 0
                self.receive_buffer = StringIO()
                return value
            except json.JSONDecodeError as e:
                # message is not complete yet
                #                logger.debug("Message not complete (%s). Buffer is: %s",
                #                             e, self.receive_buffer.getvalue())
                self.packet_counter += 1
                continue

    async def connect(self) -> None:
        self.client = BleakClient(
            self.fan, disconnected_callback=self.handle_disconnect)
        await self.client.connect()
        self.connected = True
        logger.info("Connected to %s", self.fan.name)
        await self.client.start_notify(UUID_KEY_DATA, self.handle_rx)
        logger.debug("Started notify")

        self.service = self.client.services.get_service(UUID_SERVER)
        if self.service is None:
            raise Exception("Service not found")
        logger.debug("Found service: %s", self.service.description)

        self.characteristic = self.service.get_characteristic(UUID_KEY_DATA)
        if self.characteristic is None:
            raise Exception("Characteristic not found")
        logger.debug("Found characteristic: %s",
                     self.characteristic.description)

    async def send_message(self, message: bytes) -> None:
        for s in self.sliced(message, self.characteristic.max_write_without_response_size):
            response = await self.client.write_gatt_char(
                self.characteristic, s, response=True
            )
            logger.debug("Sent %s (%d bytes), response: %s",
                         s, len(s), response)

    async def send_command(self, **kwargs) -> dict:
        payload = json.dumps(kwargs).encode("utf-8")
        await self.send_message(payload)
        return await self.get_response()

    async def login(self) -> None:
        response = await self.send_command(Api="Login", PhoneID=PAIR_ID)
        if response["Result"] == "Success":
            self.logged_in = True
            logger.info("Logged in")
        else:
            raise Exception("Login failed", response)

    async def get_fan_info(self) -> None:
        response = await self.send_command(Api="GetFanInfo")
        logger.info("Fan info: %s", response)

    async def ping_device(self) -> None:
        try:
            await self.find_fan()
            await self.connect()
            await self.login()
            await self.get_fan_info()

            await asyncio.sleep(120)
        except asyncio.exceptions.CancelledError:
            # task is cancelled on disconnect, so we ignore this error
            pass
        except Exception as e:
            logger.error("Error occurred: %s", str(e))


if __name__ == "__main__":
    fan = Fan()
    asyncio.run(fan.ping_device())
