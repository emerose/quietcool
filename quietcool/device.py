from io import StringIO
from bleak import BleakClient, BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.backends.service import BleakGATTService
import asyncio
import json
from itertools import count, takewhile
from typing import Iterator, Optional, Self
from . import logger


class Device:
    SERVICE_UUID = "000000ff-0000-1000-8000-00805f9b34fb"
    CHARACTERISTIC_UUID = "0000ff01-0000-1000-8000-00805f9b34fb"
    #    UUID_KEY_NOTIFY = "00002902-0000-1000-8000-00805f9b34fb"

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

        logger.info("Created device for fan: %s", self.fan.name)

    @classmethod
    async def find_fan(cls) -> Self:
        for attempt in range(3):
            fan = await BleakScanner.find_device_by_filter(
                lambda d, ad: d.name and d.name.startswith("ATTICFAN"), timeout=3
            )
            if fan is not None:
                ret = cls(fan)
                await ret.connect()
                return ret

            if attempt < 2:  # Don't sleep after last attempt
                logger.debug(
                    "No fan found on attempt %d, sleeping before retry...", attempt + 1
                )
                await asyncio.sleep(1)

        raise Exception("No fan found after 3 attempts")

    def sliced(self, data: bytes, n: int) -> Iterator[bytes]:
        """
        Slices *data* into chunks of size *n*. The last slice may be smaller than
        *n*.
        """
        return takewhile(len, (data[i : i + n] for i in count(0, n)))

    def handle_disconnect(self, _: BleakClient) -> None:
        logger.info("Device was disconnected, goodbye.")
        self.connected = False
        for task in asyncio.all_tasks():
            task.cancel()

    def handle_rx(self, _: BleakGATTCharacteristic, data: bytearray) -> None:
        logger.debug("received: %s", data)
        str = data.decode("utf-8")
        self.receive_buffer.write(str)
        self.data_waiting.release()

    async def get_response(self) -> dict:
        """
        Waits for and processes incoming an JSON response from the fan device.

        This method continuously accumulates received data packets until a complete,
        valid JSON message can be parsed. It uses a semaphore (self.data_waiting)
        to coordinate with the receive callback.

        Returns:
            dict: The parsed JSON response from the fan device.

        Raises:
            Exception: If the device is not connected.
            json.JSONDecodeError: Handled internally for partial messages.

        Note:
            - Resets the packet counter and receive buffer after successful parsing
            - Will keep trying to parse until a complete JSON message is received
        """
        if not self.connected:
            raise Exception("Not connected")

        while True:
            await self.data_waiting.acquire()
            try:
                value = json.loads(self.receive_buffer.getvalue())
                logger.debug(
                    "Received response %s in %d packets", value, self.packet_counter
                )
                self.packet_counter = 0
                self.receive_buffer = StringIO()
                return value
            except json.JSONDecodeError as e:
                # message is not complete yet
                self.packet_counter += 1
                continue

    async def connect(self) -> None:
        self.client = BleakClient(
            self.fan, disconnected_callback=self.handle_disconnect
        )
        await self.client.connect()
        self.connected = True
        logger.info("Connected to %s", self.fan.name)
        await self.client.start_notify(Device.CHARACTERISTIC_UUID, self.handle_rx)
        logger.debug("Started notify")

        self.service = self.client.services.get_service(Device.SERVICE_UUID)
        if self.service is None:
            raise Exception("Service not found")
        logger.debug("Found service: %s", self.service.description)

        self.characteristic = self.service.get_characteristic(
            Device.CHARACTERISTIC_UUID
        )
        if self.characteristic is None:
            raise Exception("Characteristic not found")
        logger.debug("Found characteristic: %s", self.characteristic.description)

    async def send_message(self, message: bytes) -> None:
        """
        Sends a raw byte message to the fan device, handling chunking for large messages.

        The message is automatically split into chunks based on the maximum write size
        supported by the characteristic (max_write_without_response_size).

        Args:
            message (bytes): The raw message to send to the device.

        Raises:
            Exception: If the device is not connected.
        """
        if not self.connected:
            raise Exception("Not connected")

        for s in self.sliced(
            message, self.characteristic.max_write_without_response_size
        ):
            response = await self.client.write_gatt_char(
                self.characteristic, s, response=True
            )
            logger.debug("Sent %s (%d bytes), response: %s", s, len(s), response)

    async def send_command(self, **kwargs) -> dict:
        """
        Sends a command to the device as a JSON message and waits for the response.

        This method converts the provided keyword arguments into a JSON message,
        sends it to the device, and waits for a response.

        Args:
            **kwargs: Keyword arguments that will be converted to a JSON message.
                     These represent the command and its parameters to send to the fan.

        Returns:
            dict: The parsed JSON response from the fan device.

        Raises:
            Exception: If the device is not connected.
            json.JSONDecodeError: If the response cannot be parsed as JSON.

        Example:
            response = await device.send_command(command="SetMode", Mode="Idle")
        """
        if not self.connected:
            raise Exception("Not connected")

        payload = json.dumps(kwargs).encode("utf-8")
        await self.send_message(payload)
        return await self.get_response()
