from enum import Enum
from typing import Annotated, Literal

from pydantic import BaseModel, Field
from pydantic_pint import PydanticPintQuantity
from pint import Quantity, UnitRegistry

ureg = UnitRegistry(autoconvert_offset_to_baseunit=True)


class BatterySocOffsetPercent(BaseModel):
    empty: int = Field(ge=0, le=100, default=8)
    full: int = Field(ge=0, le=100, default=8)


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
    soc_map: Literal["none", "SW102"] = Field(default="none")


class SpeedSensor(BaseModel):
    enabled: bool = Field(default=True)
    signals_per_revolution: int = Field(ge=0, default=1)


class ShiftSensor(BaseModel):
    enabled: bool = Field(default=True)
    interrupt_duration: Annotated[
        Quantity, PydanticPintQuantity("millisecond"), Field(default="600ms")
    ]
    interrupt_current_percent: int = Field(ge=0, le=100, default=10)


class TemperatureSensor(BaseModel):
    enabled: bool = Field(default=True)
    use_sensor: Literal["controller", "motor"]
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


class WalkMode(BaseModel):
    enabled: bool = Field(default=True)
    speed: Annotated[Quantity, PydanticPintQuantity("km/h"), Field(default="4km/h")]


class Pretension(BaseModel):
    enabled: bool = Field(default=False)
    speed_cutoff: Annotated[
        Quantity, PydanticPintQuantity("km/h"), Field(default="16km/h")
    ]


class LightsMode(Enum):
    default = 0
    always_on = 1
    brake_light = 2


class Lights(BaseModel):
    enabled: bool = Field(default=True)
    mode: LightsMode = Field(default=LightsMode.default)


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
    levels: list[PedalAssistLevel]


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
