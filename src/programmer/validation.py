from enum import Enum
from typing import Annotated, Literal

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field
from pydantic_pint import PydanticPintQuantity
from pint import Quantity, UnitRegistry

ureg = UnitRegistry(autoconvert_offset_to_baseunit=True)


class BatterySocOffsetPercent(BaseModel):
    empty: int = Field(ge=0, le=100, default=8)
    full: int = Field(ge=0, le=100, default=8)


class BatterySocType(Enum):
    NONE = 0
    SW102 = 1


def validate_battery_soc_type(value: str):
    try:
        return BatterySocType[value.upper()]
    except KeyError:
        raise ValueError(
            f"Not a supported battery SOC type, allowed values: {[e.name for e in BatterySocType]}"
        )


class Battery(BaseModel):
    nominal_voltage: Annotated[Quantity, PydanticPintQuantity("volt")]
    minimum_voltage: Annotated[
        Quantity, PydanticPintQuantity("volt"), Field(default="36V")
    ]
    voltage_calibration_offset: Annotated[
        Quantity, PydanticPintQuantity("volt"), Field(default="0V")
    ]
    soc_offset_percent: BatterySocOffsetPercent
    no_load_delay: Annotated[
        Quantity, PydanticPintQuantity("second"), Field(default="2s")
    ]
    low_voltage_ramp_down_percent: int = Field(ge=0, le=100, default=10)
    low_voltage_current_percent: int = Field(ge=0, le=100, default=20)
    soc_map: Annotated[
        BatterySocType,
        Field(default=BatterySocType.NONE),
        BeforeValidator(validate_battery_soc_type),
    ]

    model_config = ConfigDict(use_enum_values=True)


class SpeedSensor(BaseModel):
    enabled: bool = Field(default=True)
    signals_per_revolution: int = Field(ge=0, default=1)


class ShiftSensor(BaseModel):
    enabled: bool = Field(default=True)
    interrupt_duration: Annotated[
        Quantity, PydanticPintQuantity("millisecond"), Field(default="600ms")
    ]
    interrupt_current_percent: int = Field(ge=0, le=100, default=10)


class TemperatureSensorType(Enum):
    CONTROLLER = 0
    MOTOR = 1


def validate_temperature_sensor_type(value: str):
    try:
        return TemperatureSensorType[value.upper()]
    except KeyError:
        raise ValueError(
            f"Not a supported temperature sensor type, allowed values: {[e.name for e in TemperatureSensorType]}"
        )


class TemperatureSensor(BaseModel):
    enabled: bool = Field(default=True)
    use_sensor: Annotated[
        TemperatureSensorType,
        Field(default=TemperatureSensorType.CONTROLLER),
        BeforeValidator(validate_temperature_sensor_type),
    ]
    max_temperature: Annotated[
        Quantity,
        PydanticPintQuantity("degree_Celsius", ureg=ureg),
        Field(default="85 degC"),
    ]
    max_temperature_ramp_down_start: Annotated[
        Quantity,
        PydanticPintQuantity("degree_Celsius", ureg=ureg),
        Field(default="5 degC"),
    ]
    max_temperature_low_current_percent: int = Field(ge=0, le=100, default=20)

    model_config = ConfigDict(use_enum_values=True)


class WalkMode(BaseModel):
    enabled: bool = Field(default=True)
    speed: Annotated[Quantity, PydanticPintQuantity("km/h"), Field(default="4km/h")]


class Pretension(BaseModel):
    enabled: bool = Field(default=False)
    speed_cutoff: Annotated[
        Quantity, PydanticPintQuantity("km/h"), Field(default="16km/h")
    ]


class LightsMode(Enum):
    DEFAULT = 0
    ALWAYS_ON = 1
    BRAKE_LIGHT = 2


def validate_lights_mode(value: str):
    try:
        return LightsMode[value.upper()]
    except KeyError:
        raise ValueError(
            f"Not a supported mode type, allowed values: {[e.name for e in LightsMode]}"
        )


class Lights(BaseModel):
    enabled: bool = Field(default=True)
    mode: Annotated[
        LightsMode,
        Field(default=LightsMode.DEFAULT),
        BeforeValidator(validate_lights_mode),
    ]

    model_config = ConfigDict(use_enum_values=True)


class PedalAssistLevel(BaseModel):
    flags: str = Field(default="ASSIST_FLAG_NONE")
    max_cadence_percent: int = Field(ge=0, le=100, default=0)
    max_pas_speed: Annotated[
        Quantity, PydanticPintQuantity("km/h"), Field(default="0km/h")
    ]
    target_power_watts: int = Field(ge=0, default=0)
    max_throttle_speed: Annotated[
        Quantity, PydanticPintQuantity("km/h"), Field(default="0km/h")
    ]
    max_throttle_power_watts: int = Field(ge=0, default=0)


class PedalAssistLevelType(BaseModel):
    levels: list[PedalAssistLevel] = Field(min_length=9, max_length=9)


class PedalAssistLevels(BaseModel):
    standard: PedalAssistLevelType
    sport: PedalAssistLevelType


class Config(BaseModel):
    motor_type: Literal["BBSHD", "BBS02_750W", "BBS02_500W"]
    max_current: Annotated[Quantity, PydanticPintQuantity("ampere")]
    global_max_speed: Annotated[Quantity, PydanticPintQuantity("km/h")]
    wheel_circumference: Annotated[Quantity, PydanticPintQuantity("millimeter")]
    battery: Battery
    speed_sensor: SpeedSensor
    shift_sensor: ShiftSensor
    temperature_sensor: TemperatureSensor
    walk_mode: WalkMode
    pretension: Pretension
    lights: Lights
    pedal_assist_levels: PedalAssistLevels
