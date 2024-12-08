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
        print(await self.api.testcmd())
