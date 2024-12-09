from typing import Optional, Self

from .api import Api
from .device import Device
from . import logger


class Client:
    """
    Client for the QuietCool QuietFan API.

    WARNING: Don't instantiate this class directly, use the create method.
    """

    def __init__(self, api_id: str) -> None:
        self.api_id = api_id
        self.device: Optional[Device] = None
        self.api: Optional[Api] = None

    @classmethod
    async def create(cls, api_id: str) -> Self:
        """
        Create and connect a new Client instance.

        Args:
            api_id: The API ID to use for authentication

        Returns:
            A connected Client instance
        """
        client = cls(api_id)
        await client.connect()
        return client

    async def connect(self) -> None:
        self.device = await Device.find_fan()
        self.api = Api(self.device, self.api_id)
        await self.api.login()

    async def doit(self) -> None:
        #        print(await self.api.testcmd())

        # Get all states and info

        reset_response = await self.api.reset()
        print(f"Reset Response: {reset_response}")

        set_fan_info = await self.api.set_fan_info()
        print(f"Set Fan Info Response: {set_fan_info}")

        set_guide = await self.api.set_guide_setup()
        print(f"Set Guide Setup Response: {set_guide}")

        set_mode = await self.api.set_mode()
        print(f"Set Mode Response: {set_mode}")

        set_presets = await self.api.set_presets()
        print(f"Set Presets Response: {set_presets}")

        set_router = await self.api.set_router()
        print(f"Set Router Response: {set_router}")

        set_temp = await self.api.set_temp_humidity()
        print(f"Set Temp Humidity Response: {set_temp}")

        set_time = await self.api.set_time()
        print(f"Set Time Response: {set_time}")
