from typing import Optional

from .api import Api
from .device import Device


class Client:
    def __init__(self, api_id: str) -> None:
        self.api_id = api_id
        self.device: Optional[Device] = None
        self.api: Optional[Api] = None

    async def connect(self) -> None:
        self.device = await Device.find_fan()
        self.api = Api(self.device, self.api_id)
        await self.api.login()

    async def doit(self) -> None:
        print(await self.api.testcmd())
