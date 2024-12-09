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
        # the android app does this:
        # login
        # get fan info
        # get parameters
        # get version
        # get presets
        # get fan info (again)
        # get work state (mode is Idle)
        # set guide setup = no

        workstate = await self.api.get_work_state()
        print(workstate)

# activate smart mode looks like:
# set mode mode=TH
# get work state (again) now mode is TH

# activate timer mode looks like:
# set mode mode=Timer
# get work state (again) now mode is Timer
# get remain time

# turning either of those modes off looks like:
# set mode mode=Idle
# get work state; now mode is Idle

# setting fan info looks like:
# GetFanInfo
# SetFanInfo: response has Flag=TRUE
# GetFanInfo: response is updated

# upgrade firmware looks like:
# Upgrade with URL; response has Flag=TRUE
# SetRouter; response has Flag=TRUE
# poll GetUpgradeState for updates
