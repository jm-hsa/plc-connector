from dataclasses import dataclass, field

from .common import BaseMeasurement

@dataclass(frozen=True)
class Measurement24v(BaseMeasurement):
  current: tuple # [float, ...]
  status: tuple # [bool, ...]
  overload: tuple # [bool, ...]
  short_circuit: tuple # [bool, ...]
  limit: tuple # [bool, ...]
  pushbutton: tuple # [bool, ...]
  voltage: float

  series: str = field(default="24v")

@dataclass(frozen=True)
class Measurement480v(BaseMeasurement):
  voltage: tuple # [float, ...]
  current: tuple # [float, ...]
  phase: tuple # [float, ...]

  series: str = field(default="480v")