from dataclasses import dataclass, field
from structures.common import BaseMeasurement

@dataclass(frozen=True)
class CorrelatedMeasurements(BaseMeasurement):
  series: str = field(default="correlated", init=False)
  measurement_24v: BaseMeasurement
  measurement_480v: BaseMeasurement
  measurement_plant: BaseMeasurement