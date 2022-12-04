from dataclasses import dataclass, field
from datetime import datetime
from typing import Hashable

@dataclass(frozen=True)
class BaseMeasurement(Hashable):
  timestamp: datetime
  source: str
  #series: str = field(init=False)