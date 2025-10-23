from enum import Enum
from typing import Annotated

from pydantic import (
    AfterValidator,
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    model_validator,
)
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
    maximum_voltage: Annotated[Quantity, PydanticPintQuantity("centivolt", ureg=ureg)]
    minimum_voltage: Annotated[
        Quantity, PydanticPintQuantity("volt", ureg=ureg), Field(default="36V")
    ]
    voltage_calibration_offset: Annotated[
        Quantity, PydanticPintQuantity("volt", ureg=ureg), Field(default="0V")
    ]
    soc_offset_percent: BatterySocOffsetPercent
    no_load_delay: Annotated[
        Quantity, PydanticPintQuantity("second", ureg=ureg), Field(default="2s")
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
        Quantity, PydanticPintQuantity("millisecond", ureg=ureg), Field(default="600ms")
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
    speed: Annotated[
        Quantity, PydanticPintQuantity("km/h", ureg=ureg), Field(default="4km/h")
    ]


class Pretension(BaseModel):
    enabled: bool = Field(default=False)
    speed_cutoff: Annotated[
        Quantity, PydanticPintQuantity("km/h", ureg=ureg), Field(default="16km/h")
    ]


class LightsMode(Enum):
    DEFAULT = 0
    ALWAYS_ON = 1
    BRAKE_LIGHT = 2
    DEFAULT_AND_BRAKE_LIGHT = 3


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
        Quantity, PydanticPintQuantity("km/h", ureg=ureg), Field(default="0km/h")
    ]
    target_power_watts: int = Field(ge=0, default=0)
    max_throttle_speed: Annotated[
        Quantity, PydanticPintQuantity("km/h", ureg=ureg), Field(default="0km/h")
    ]
    max_throttle_power_watts: int = Field(ge=0, default=0)


def validate_pas_level_counts(value: list[PedalAssistLevel]):
    if len(value) == 10:
        return value
    if len(value) == 6:
        return [
            value[0],
            value[1],
            value[1],
            value[2],
            value[2],
            value[3],
            value[3],
            value[4],
            value[4],
            value[5],
        ]
    if len(value) == 4:
        return [
            value[0],
            value[1],
            value[1],
            value[1],
            value[1],
            value[2],
            value[2],
            value[2],
            value[2],
            value[3],
        ]
    raise ValueError(
        "Must provide either 3, 5 or 9 pedal assist levels, along with PAS 0"
    )


class PedalAssistLevelType(BaseModel):
    levels: Annotated[
        list[PedalAssistLevel],
        Field(max_length=10),
        AfterValidator(validate_pas_level_counts),
    ]


class PedalAssistLevels(BaseModel):
    standard: PedalAssistLevelType
    sport: PedalAssistLevelType


class MotorType(Enum):
    BBSHD = 0
    BBS02_750W = 1
    BBS02_500W = 2


def validate_motor_type(value: str):
    try:
        return MotorType[value.upper()]
    except KeyError:
        raise ValueError(
            f"Not a supported motor type, allowed values: {[e.name for e in MotorType]}"
        )


class Config(BaseModel):
    motor_type: Annotated[
        MotorType,
        BeforeValidator(validate_motor_type),
    ]

    max_current: Annotated[
        Quantity | None, PydanticPintQuantity("ampere", ureg=ureg), Field(default=None)
    ]
    current_ramp_per_second: Annotated[
        Quantity, PydanticPintQuantity("ampere", ureg=ureg)
    ]
    prefer_imperial_units: bool = Field(default=False)
    wheel_circumference: Annotated[
        Quantity, PydanticPintQuantity("millimeter", ureg=ureg)
    ]
    display_wheel_diameter: Annotated[
        Quantity | None, PydanticPintQuantity("inch", ureg=ureg), Field(default=None)
    ]
    speed_limit_sport_switch: Annotated[
        Quantity | None, PydanticPintQuantity("km/h", ureg=ureg), Field(default=None)
    ]
    battery: Battery
    speed_sensor: SpeedSensor
    shift_sensor: ShiftSensor
    temperature_sensor: TemperatureSensor
    walk_mode: WalkMode
    pretension: Pretension
    lights: Lights
    pedal_assist_levels: PedalAssistLevels

    model_config = ConfigDict(use_enum_values=True)

    @model_validator(mode="after")
    def check_max_current(self):
        motor_current_limits = {
            MotorType.BBSHD.value: 30 * ureg.ampere,
            MotorType.BBS02_750W.value: 25 * ureg.ampere,
            MotorType.BBS02_500W.value: 20 * ureg.ampere,
        }
        max_motor_current = motor_current_limits[self.motor_type]
        # If the user does not specify the maximum current, set the max current to the limit.
        if self.max_current is None:
            self.max_current = max_motor_current
        # If the user does specify it, check and fail if it is above the limit
        elif self.max_current > max_motor_current:
            raise ValueError(
                f"Motor max current cannot be above the limit of {max_motor_current} for motor type {self.motor_type}"
            )
        return self

    @model_validator(mode="after")
    def check_temperature_sensor(self):
        if (
            self.temperature_sensor.use_sensor == TemperatureSensorType.MOTOR.value
            and self.motor_type != "BBSHD"
        ):
            raise ValueError(
                "Temperature sensor type Motor is only available on motor type BBSHD"
            )
        return self
