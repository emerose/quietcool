from .device import Device
import logging
from dataclasses import dataclass
from typing import Self


@dataclass
class FanInfo:
    name: str
    model: str
    serial_num: str

    @classmethod
    def from_response(cls, response: dict) -> Self:
        return cls(
            name=response['Name'],
            model=response['Model'],
            serial_num=response['SerialNum']
        )


@dataclass
class VersionInfo:
    version: str
    protect_temp: int
    create_date: str
    create_mode: str
    hw_version: str

    @classmethod
    def from_response(cls, response: dict) -> Self:
        return cls(
            version=response["Version"],
            protect_temp=response["ProtectTemp"],
            create_date=response["Create_Date"],
            create_mode=response["Create_Mode"],
            hw_version=response["HW_Version"]
        )


@dataclass
class ParameterInfo:
    mode: str
    fan_type: str
    temp_high: int
    temp_medium: int
    temp_low: int
    humidity_high: int
    humidity_low: int
    humidity_range: str
    hour: int
    minute: int
    time_range: str

    @classmethod
    def from_response(cls, response: dict) -> Self:
        return cls(
            mode=response['Mode'],
            fan_type=response['FanType'],
            temp_high=response['GetTemp_H'],
            temp_medium=response['GetTemp_M'],
            temp_low=response['GetTemp_L'],
            humidity_high=response['GetHum_H'],
            humidity_low=response['GetHum_L'],
            humidity_range=response['GetHum_Range'],
            hour=response['GetHour'],
            minute=response['GetMinute'],
            time_range=response['GetTime_Range']
        )


class Api:
    def __init__(self, device: Device) -> None:
        self.device = device
        self.logged_in = False
        self.logger = logging.getLogger(__name__)

    async def login(self, pair_id: str) -> None:
        response = await self.device.send_command(Api="Login", PhoneID=pair_id)
        if response["Result"] == "Success":
            self.logged_in = True
            self.logger.info("Logged in")
        else:
            raise Exception("Login failed", response)

    async def get_fan_info(self) -> FanInfo:
        response = await self.device.send_command(Api="GetFanInfo")
        fan_info = FanInfo.from_response(response)
        self.logger.debug("Fan info: %s", fan_info)
        return fan_info

    async def get_version(self) -> VersionInfo:
        response = await self.device.send_command(Api="GetVersion")
        version_info = VersionInfo.from_response(response)
        self.logger.debug("Version info: %s", version_info)
        return version_info

    async def get_parameter(self) -> ParameterInfo:
        response = await self.device.send_command(Api="GetParameter")
        parameter_info = ParameterInfo.from_response(response)
        self.logger.debug("Parameter: %s", parameter_info)
        return parameter_info
