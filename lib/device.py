from io import StringIO
from bleak import BleakClient, BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.backends.service import BleakGATTService
import asyncio
import json
from itertools import count, takewhile
from typing import Iterator, Optional, Self
import logging


class Device:
    UUID_SERVER = "000000ff-0000-1000-8000-00805f9b34fb"
    UUID_KEY_DATA = "0000ff01-0000-1000-8000-00805f9b34fb"
    UUID_KEY_NOTIFY = "00002902-0000-1000-8000-00805f9b34fb"

    def __init__(self, fan: BLEDevice) -> None:
        self.fan: BLEDevice = fan
        self.send_buffer: StringIO = StringIO()
        self.receive_buffer: StringIO = StringIO()
        self.connected: bool = False
        self.client: Optional[BleakClient] = None
        self.service: Optional[BleakGATTService] = None
        self.characteristic: Optional[BleakGATTCharacteristic] = None
        self.data_waiting: asyncio.Semaphore = asyncio.Semaphore(0)
        self.packet_counter: int = 0
        self.logger = logging.getLogger(__name__)

        self.logger.info("Created device for fan: %s", self.fan.name)

    @classmethod
    async def find_fan(cls) -> Self:
        fan = await BleakScanner.find_device_by_filter(
            lambda d, ad: d.name and d.name.startswith("ATTICFAN"), timeout=3
        )
        if fan is None:
            raise Exception("No fan found")
        ret = cls(fan)
        await ret.connect()
        return ret

    def sliced(self, data: bytes, n: int) -> Iterator[bytes]:
        """
        Slices *data* into chunks of size *n*. The last slice may be smaller than
        *n*.
        """
        return takewhile(len, (data[i: i + n] for i in count(0, n)))

    def handle_disconnect(self, _: BleakClient) -> None:
        self.logger.info("Device was disconnected, goodbye.")
        self.connected = False
        for task in asyncio.all_tasks():
            task.cancel()

    def handle_rx(self, _: BleakGATTCharacteristic, data: bytearray) -> None:
        self.logger.debug("received: %s", data)
        str = data.decode('utf-8')
        self.receive_buffer.write(str)
        self.data_waiting.release()

    async def get_response(self) -> dict:
        if not self.connected:
            raise Exception("Not connected")

        while True:
            await self.data_waiting.acquire()
            try:
                value = json.loads(self.receive_buffer.getvalue())
                self.logger.debug("Received response %s in %d packets",
                                  value, self.packet_counter)
                self.packet_counter = 0
                self.receive_buffer = StringIO()
                return value
            except json.JSONDecodeError as e:
                # message is not complete yet
                self.packet_counter += 1
                continue

    async def connect(self) -> None:
        self.client = BleakClient(
            self.fan, disconnected_callback=self.handle_disconnect)
        await self.client.connect()
        self.connected = True
        self.logger.info("Connected to %s", self.fan.name)
        await self.client.start_notify(Device.UUID_KEY_DATA, self.handle_rx)
        self.logger.debug("Started notify")

        self.service = self.client.services.get_service(Device.UUID_SERVER)
        if self.service is None:
            raise Exception("Service not found")
        self.logger.debug("Found service: %s", self.service.description)

        self.characteristic = self.service.get_characteristic(
            Device.UUID_KEY_DATA)
        if self.characteristic is None:
            raise Exception("Characteristic not found")
        self.logger.debug("Found characteristic: %s",
                          self.characteristic.description)

    async def send_message(self, message: bytes) -> None:
        if not self.connected:
            raise Exception("Not connected")

        for s in self.sliced(message, self.characteristic.max_write_without_response_size):
            response = await self.client.write_gatt_char(
                self.characteristic, s, response=True
            )
            self.logger.debug("Sent %s (%d bytes), response: %s",
                              s, len(s), response)

    async def send_command(self, **kwargs) -> dict:
        if not self.connected:
            raise Exception("Not connected")

        payload = json.dumps(kwargs).encode("utf-8")
        await self.send_message(payload)
        return await self.get_response()
