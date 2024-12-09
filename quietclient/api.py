from .device import Device
from . import logger
from dataclasses import dataclass, asdict
from typing import Self, Any, TypeAlias
from enum import Enum
import json


class LoginError(Exception):
    """Raised when login to the fan device fails."""
    pass


class DataclassJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, '__dataclass_fields__'):
            return asdict(obj)
        return super().default(obj)


@dataclass
class FanInfo:
    """
    Information about a fan device.

    Attributes:
        name: The fan's name
        model: The fan's model number
        serial_num: The fan's serial number
    """
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
class PairModeResponse:
    response: dict

    @classmethod
    def from_response(cls, response: dict) -> Self:
        return cls(response=response)


@dataclass
class PairResponse:
    response: dict

    @classmethod
    def from_response(cls, response: dict) -> Self:
        return cls(response=response)


@dataclass
class Parameters:
    """
    Fan operating parameters.

    Attributes:
        mode: Current operating mode
        fan_type: Type of fan
        temp_high: High temperature threshold
        temp_medium: Medium temperature threshold
        temp_low: Low temperature threshold
        humidity_high: High humidity threshold
        humidity_low: Low humidity threshold
        humidity_range: Humidity range setting
        hour: Hour setting
        minute: Minute setting
        time_range: Time range setting
    """
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
    """
    Fan preset configuration.

    Attributes:
        name: Preset name
        temp_high: High temperature threshold
        temp_med: Medium temperature threshold
        temp_low: Low temperature threshold
        humidity_off: Humidity off threshold
        humidity_on: Humidity on threshold
        humidity_speed: Fan speed for humidity control
    """
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
    """
    Remaining time information. (???)

    Attributes:
        hours: Hours remaining
        minutes: Minutes remaining
        seconds: Seconds remaining
    """
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
class ResetResponse:
    response: dict

    @classmethod
    def from_response(cls, response: dict) -> Self:
        return cls(response=response)


@dataclass
class SetFanInfoResponse:
    response: dict

    @classmethod
    def from_response(cls, response: dict) -> Self:
        return cls(response=response)


@dataclass
class SetGuideSetupResponse:
    response: dict

    @classmethod
    def from_response(cls, response: dict) -> Self:
        return cls(response=response)


@dataclass
class SetModeResponse:
    response: dict

    @classmethod
    def from_response(cls, response: dict) -> Self:
        return cls(response=response)


@dataclass
class SetPresetsResponse:
    response: dict

    @classmethod
    def from_response(cls, response: dict) -> Self:
        return cls(response=response)


@dataclass
class SetRouterResponse:
    response: dict

    @classmethod
    def from_response(cls, response: dict) -> Self:
        return cls(response=response)


@dataclass
class SetTempHumidityResponse:
    response: dict

    @classmethod
    def from_response(cls, response: dict) -> Self:
        return cls(response=response)


@dataclass
class SetTimeResponse:
    response: dict

    @classmethod
    def from_response(cls, response: dict) -> Self:
        return cls(response=response)


@dataclass
class UpgradeResponse:
    flag: str

    @classmethod
    def from_response(cls, response: dict) -> Self:
        return cls(
            flag=response['Flag']
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
class VersionInfo:
    """
    Version information for the fan.

    Attributes:
        version: Software version
        protect_temp: Protection temperature threshold
        create_date: Creation date
        create_mode: Creation mode
        hw_version: Hardware version
    """
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
class WorkState:
    """
    Current working state of the fan.

    Attributes:
        mode: Current operating mode
        range: Operating range
        sensor_state: State of the sensors
        temperature: Current temperature
        humidity: Current humidity percentage
    """
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


class GuideSetup(str, Enum):
    """Guide setup state options."""
    YES = "YES"
    NO = "NO"


class Mode(str, Enum):
    """Fan operating mode options."""
    IDLE = "Idle"


class HumidityRange(str, Enum):
    """Humidity range setting options."""
    HIGH = "HIGH"
    LOW = "LOW"


class Api:
    """
    API client for interacting with the fan device.

    Attributes:
        device: The fan device instance
        pair_id: The pairing ID for authentication
        logged_in: Whether the client is currently logged in
    """

    def __init__(self, device: Device, pair_id: str) -> None:
        self.device = device
        self.pair_id = pair_id
        self.logged_in = False

    async def login(self) -> None:
        """
        Login to the fan device.

        Returns:
            None

        Raises:
            LoginError: If the login fails
        """
        response = await self.device.send_command(Api="Login", PhoneID=self.pair_id)
        # response will be something like:
        # {"Api": "Login", "Result": "Success", "PairState": "No"}
        # or
        # {"Api": "Login", "Result": "Fail", "PairState": "No"}
        if response["Result"] == "Success":
            self.logged_in = True
            logger.info("Logged in")
        else:
            raise LoginError(f"Login failed: {response}")

    async def ensure_logged_in(self) -> None:
        """
        Ensure the client is logged in.

        Returns:
            None

        Raises:
            Exception: If the login fails
        """
        if not self.logged_in:
            await self.login()

    async def get_fan_info(self) -> FanInfo:
        """
        Retrieve information about the fan.

        Returns:
            FanInfo object containing name, model, and serial number
        """
        await self.ensure_logged_in()

        response = await self.device.send_command(Api="GetFanInfo")
        fan_info = FanInfo.from_response(response)
        logger.debug("Fan info: %s", fan_info)
        return fan_info

    async def get_parameters(self) -> Parameters:
        """
        Retrieve current fan parameters.

        Returns:
            Parameters object containing current fan settings
        """
        await self.ensure_logged_in()

        response = await self.device.send_command(Api="GetParameter")
        parameter_info = Parameters.from_response(response)
        logger.debug("Parameter: %s", parameter_info)
        return parameter_info

    async def get_presets(self) -> PresetList:
        """
        Retrieve list of fan presets.

        Returns:
            List of Preset objects
        """
        await self.ensure_logged_in()

# TODO: the android app passes "FanType":"THREE" here
        response = await self.device.send_command(Api="GetPresets")
        presets = [Preset.from_response(preset)
                   for preset in response["Presets"]]
        logger.debug("Presets: %s", presets)
        return presets

    async def get_remain_time(self) -> RemainTime:
        """
        Retrieve remaining time information.

        No idea what "remaining time" is for.

        Returns:
            RemainTime object with hours, minutes, and seconds
        """
        await self.ensure_logged_in()

        response = await self.device.send_command(Api="GetRemainTime")
        remain_time = RemainTime.from_response(response)
        logger.debug("Remain time: %s", remain_time)
        return remain_time

    async def get_upgrade_state(self) -> UpgradeState:
        """
        Retrieve the current upgrade state.

        No idea what this refers to

        Returns:
            UpgradeState object containing the current state
        """
        await self.ensure_logged_in()

        response = await self.device.send_command(Api="GetUpgradeState")
        upgrade_state = UpgradeState.from_response(response)
        logger.debug("Upgrade state: %s", upgrade_state)
        return upgrade_state

    async def get_version(self) -> VersionInfo:
        """
        Retrieve version information.

        Returns:
            VersionInfo object containing version details
        """
        await self.ensure_logged_in()

        response = await self.device.send_command(Api="GetVersion")
        version_info = VersionInfo.from_response(response)
        logger.debug("Version info: %s", version_info)
        return version_info

    async def get_work_state(self) -> WorkState:
        """
        Retrieve current working state.

        Returns:
            WorkState object containing current operational status
        """
        await self.ensure_logged_in()

        response = await self.device.send_command(Api="GetWorkState")
        work_state = WorkState.from_response(response)
        logger.debug("Work state: %s", work_state)
        return work_state

    async def pair(self, pair_id: str) -> PairResponse:
        """
        Add a new pairing ID to the fan. Fan must be in pairing mode already.

        Args:
            pair_id: The pairing ID to add to the fan

        Returns:
            PairResponse containing the result
        """
        await self.ensure_logged_in()
        response = await self.device.send_command(Api="Pair", PhoneID=pair_id)
        return PairResponse.from_response(response)

    async def pair_mode(self) -> PairModeResponse:
        """
        Tell the fan to enter pairing mode.

        Returns:
            PairModeResponse containing the result
        """
        await self.ensure_logged_in()
        response = await self.device.send_command(Api="PairMode")
        return PairModeResponse.from_response(response)

    async def reset(self) -> ResetResponse:
        """
        Reset the fan. (???)

        Unclear if this resets the device or just something about BLE

        Returns:
            ResetResponse containing the result
        """
        await self.ensure_logged_in()
        response = await self.device.send_command(Api="Reset")
        return ResetResponse.from_response(response)

    async def set_fan_info(self, name: str, model: str, serial_num: str) -> SetFanInfoResponse:
        """
        Set fan information.

        Args:
            name: New fan name
            model: Fan model number
            serial_num: Fan serial number

        Returns:
            SetFanInfoResponse containing the result
        """
        await self.ensure_logged_in()
        response = await self.device.send_command(
            Api="SetFanInfo",
            Name=name,
            Model=model,
            SerialNum=serial_num
        )
        return SetFanInfoResponse.from_response(response)

    async def set_guide_setup(self, guide_setup: GuideSetup) -> SetGuideSetupResponse:
        """
        Set the guide setup state.

        Args:
            guide_setup: The guide setup state to set (GuideSetup.YES or GuideSetup.NO)

        Returns:
            SetGuideSetupResponse containing the result
        """
        await self.ensure_logged_in()
        response = await self.device.send_command(Api="SetGuideSetup", GuideSetup=guide_setup)
        return SetGuideSetupResponse.from_response(response)

    # TODO: the android app passes "Mode":"TH" here
    # it gets a response like: {"Api": "SetMode", "WorkMode": "TH", "Flag": "TRUE"}
    async def set_mode(self, mode: Mode) -> SetModeResponse:
        """
        Set the fan's operating mode.

        Args:
            mode: The mode to set (e.g., Mode.IDLE)

        Returns:
            SetModeResponse containing the result
        """
        await self.ensure_logged_in()
        response = await self.device.send_command(Api="SetMode", Mode=mode)
        # TODO: check that Flag is TRUE
        return SetModeResponse.from_response(response)

    async def set_presets(self) -> SetPresetsResponse:
        await self.ensure_logged_in()
        response = await self.device.send_command(Api="SetPresets")
        return SetPresetsResponse.from_response(response)

    async def set_router(self, ssid: str, password: str) -> SetRouterResponse:
        """
        Set the WiFi router credentials. (???)

        Args:
            ssid: The WiFi network SSID
            password: The WiFi network password

        Returns:
            SetRouterResponse containing the result
        """
        await self.ensure_logged_in()
        response = await self.device.send_command(
            Api="SetRouter",
            Ssid=ssid,
            Password=password
        )
        return SetRouterResponse.from_response(response)

    async def set_temp_humidity(
        self,
        temp_high: int,
        temp_medium: int,
        temp_low: int,
        humidity_high: int,
        humidity_low: int,
        humidity_range: HumidityRange
    ) -> SetTempHumidityResponse:
        """
        Set temperature and humidity parameters.

        Args:
            temp_high: High temperature threshold
            temp_medium: Medium temperature threshold
            temp_low: Low temperature threshold
            humidity_high: High humidity threshold
            humidity_low: Low humidity threshold
            humidity_range: Humidity range setting (HumidityRange.HIGH or HumidityRange.LOW)

        Returns:
            SetTempHumidityResponse containing the result
        """
        await self.ensure_logged_in()
        response = await self.device.send_command(
            Api="SetTempHumidity",
            SetTemp_H=temp_high,
            SetTemp_M=temp_medium,
            SetTemp_L=temp_low,
            SetHum_H=humidity_high,
            SetHum_L=humidity_low,
            SetHum_Range=humidity_range
        )
        return SetTempHumidityResponse.from_response(response)

    async def set_time(self, hour: int, minute: int, time_range: str) -> SetTimeResponse:
        """
        Set the time parameters.

        Args:
            hour: Hour value (0-23)
            minute: Minute value (0-59)
            time_range: Time range setting

        Returns:
            SetTimeResponse containing the result
        """
        await self.ensure_logged_in()
        response = await self.device.send_command(
            Api="SetTime",
            SetHour=hour,
            SetMinute=minute,
            SetTime_Range=time_range
        )
        return SetTimeResponse.from_response(response)

    async def upgrade(self, url: str) -> UpgradeResponse:
        """
        Initiate a firmware upgrade from the specified URL.

        Args:
            url: The URL to download the firmware from

        Returns:
            UpgradeResponse containing the result
        """
        await self.ensure_logged_in()
        response = await self.device.send_command(Api="Upgrade", URL=url)
        return UpgradeResponse.from_response(response)
