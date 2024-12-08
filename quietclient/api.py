from .device import Device
from . import logger
from dataclasses import dataclass
from typing import Self, Any, TypeAlias


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
class Parameters:
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


@dataclass
class Preset:
    name: str
    temp_high: int
    temp_med: int
    temp_low: int
    humidity_off: int
    humidity_on: int
    humidity_speed: str

    @classmethod
    def from_response(cls, response: list) -> Self:
        return cls(
            name=response[0],
            temp_high=response[1],
            temp_med=response[2],
            temp_low=response[3],
            humidity_off=response[4],
            humidity_on=response[5],
            humidity_speed=response[6]
        )


PresetList: TypeAlias = list[Preset]


@dataclass
class RemainTime:
    hours: int
    minutes: int
    seconds: int

    @classmethod
    def from_response(cls, response: dict) -> Self:
        return cls(
            hours=response['RemainHour'],
            minutes=response['RemainMinute'],
            seconds=response['RemainSecond']
        )


@dataclass
class UpgradeState:
    state: str

    @classmethod
    def from_response(cls, response: dict) -> Self:
        return cls(
            state=response['State']
        )


@dataclass
class WorkState:
    mode: str
    range: str
    sensor_state: str
    temperature: float
    humidity: int

    @classmethod
    def from_response(cls, response: dict) -> Self:
        return cls(
            mode=response['Mode'],
            range=response['Range'],
            sensor_state=response['SensorState'],
            temperature=response['Temp_Sample'] / 10,
            humidity=response['Humidity_Sample']
        )


class Api:
    def __init__(self, device: Device, pair_id: str) -> None:
        self.device = device
        self.pair_id = pair_id
        self.logged_in = False

    async def login(self) -> None:
        response = await self.device.send_command(Api="Login", PhoneID=self.pair_id)
        if response["Result"] == "Success":
            self.logged_in = True
            logger.info("Logged in")
        else:
            raise Exception("Login failed", response)

    async def ensure_logged_in(self) -> None:
        if not self.logged_in:
            await self.login()

    async def get_fan_info(self) -> FanInfo:
        await self.ensure_logged_in()

        response = await self.device.send_command(Api="GetFanInfo")
        fan_info = FanInfo.from_response(response)
        logger.debug("Fan info: %s", fan_info)
        return fan_info

    async def get_parameter(self) -> Parameters:
        await self.ensure_logged_in()

        response = await self.device.send_command(Api="GetParameter")
        parameter_info = Parameters.from_response(response)
        logger.debug("Parameter: %s", parameter_info)
        return parameter_info

    async def get_presets(self) -> PresetList:
        await self.ensure_logged_in()

        response = await self.device.send_command(Api="GetPresets")
        presets = [Preset.from_response(preset)
                   for preset in response["Presets"]]
        logger.debug("Presets: %s", presets)
        return presets

    async def get_remain_time(self) -> RemainTime:
        await self.ensure_logged_in()

        response = await self.device.send_command(Api="GetRemainTime")
        remain_time = RemainTime.from_response(response)
        logger.debug("Remain time: %s", remain_time)
        return remain_time

    async def get_upgrade_state(self) -> UpgradeState:
        await self.ensure_logged_in()

        response = await self.device.send_command(Api="GetUpgradeState")
        upgrade_state = UpgradeState.from_response(response)
        logger.debug("Upgrade state: %s", upgrade_state)
        return upgrade_state

    async def get_version(self) -> VersionInfo:
        await self.ensure_logged_in()

        response = await self.device.send_command(Api="GetVersion")
        version_info = VersionInfo.from_response(response)
        logger.debug("Version info: %s", version_info)
        return version_info

    async def get_work_state(self) -> WorkState:
        await self.ensure_logged_in()

        response = await self.device.send_command(Api="GetWorkState")
        work_state = WorkState.from_response(response)
        logger.debug("Work state: %s", work_state)
        return work_state

    async def testcmd(self) -> Any:
        await self.ensure_logged_in()

        response = await self.device.send_command(Api="GetWorkState")
        logger.info("Work state: %s", response)

        return response
