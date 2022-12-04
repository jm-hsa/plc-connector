from dataclasses import dataclass, field

from .common import BaseMeasurement

@dataclass(frozen=True)
class CompactLogixState(BaseMeasurement):
  field1: int
  field2: bool

  series: str = field(default="plant")

@dataclass(frozen=True)
class S7State(BaseMeasurement):
  cpu_running: bool
  
  field1: int
  field2: bool

  series: str = field(default="plant", init=False)
