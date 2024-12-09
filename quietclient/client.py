from typing import Optional, Self
import os
import pathlib

from .api import Api
from .device import Device
from . import logger


class Client:
    """
    Client for the QuietCool QuietFan API.

    WARNING: Don't instantiate this class directly, use the create method.
    """

    def __init__(self, api_id: str, device: Device) -> None:
        self.api_id = api_id
        self.device = device
        self.api = Api(self.device, self.api_id)

    @classmethod
    async def create(cls, api_id: Optional[str] = None, device: Optional[Device] = None) -> Self:
        """
        Create a new Client instance.

        Args:
            api_id: The API ID to use for authentication. If not provided, will check:
                   1. QUIETCOOL environment variable
                   2. /etc/quietcool file
                   3. ~/.quietcool file
                   4. ./.quietcool file
                   The first found value will be used.
            device: Optional Device instance. If not provided, will attempt to discover
                   a fan on the network using Device.find_fan()

        Returns:
            A connected Client instance

        Raises:
            ValueError: If no API ID is provided and none can be found in the expected locations
        """
        if api_id is None:
            api_id = cls._find_api_id()

        if device is None:
            device = await Device.find_fan()

        client = cls(api_id, device)
        return client

    @staticmethod
    def _find_api_id() -> str:
        # Check environment variable
        if api_id := os.environ.get("QUIETCOOL"):
            return api_id

        # Check config files in order
        config_paths = [
            pathlib.Path("/etc/quietcool"),
            pathlib.Path.home() / ".quietcool",
            pathlib.Path(".quietcool"),
        ]

        for path in config_paths:
            if path.is_file():
                api_id = path.read_text().strip()
                if api_id:
                    return api_id

        raise ValueError(
            "No API ID provided and none found in environment or config files")

    async def pair(self) -> None:
        login_result = await self.api.send_login()
        if login_result["Result"] == "Success":
            print("Already paired")
            return
        elif login_result["PairState"] == "No":
            print("Not in pairing mode")
            return
        print("Pairing...")
        result = await self.api.pair(self.api_id)
        if result:
            print("Pairing successful")
        else:
            print("Pairing failed")

    async def get_info(self) -> dict:
        faninfo = await self.api.get_fan_info()
        params = await self.api.get_parameters()
        version = await self.api.get_version()
        presets = await self.api.get_presets()
        workstate = await self.api.get_work_state()
        return {
            "faninfo": faninfo,
            "params": params,
            "version": version,
            "presets": presets,
            "workstate": workstate,
        }

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
