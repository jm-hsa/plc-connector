from dataclasses import fields

from structures.common import BaseMeasurement
from structures.measurement import Measurement24v, Measurement480v
from structures.plant import S7State, CompactLogixState
from structures.correlated import CorrelatedMeasurements

class MatchSeries:
  def __init__(self, series) -> None:
    self._series = series
  
  def get_series(self, measurement: BaseMeasurement):
    if measurement.series == self._series:
      return measurement
    else:
      # find the series in the data
      for key, value in measurement.__dict__.items():
        if isinstance(value, BaseMeasurement) and value.series == self._series:
          return value

  def set_series(self, measurement: BaseMeasurement, series: BaseMeasurement):
    if measurement.series == self._series:
      return series
    else:
      # find the series in the data
      for key, value in measurement.__dict__.items():
        if isinstance(value, BaseMeasurement) and value.series == self._series:
          return type(measurement)(**{**measurement.__dict__, key: series})

ALLOWED_GLOBALS = {
  'sum': sum,
  'min': min,
  'max': max,
  'avg': lambda x: sum(x) / len(x),
  'count': len,
  'last': lambda x: x[-1],
}

ALLOWED_NAMES = \
  [x.name for x in fields(Measurement24v)] + \
  [x.name for x in fields(Measurement480v)] + \
  [x.name for x in fields(CompactLogixState)] + \
  [x.name for x in fields(S7State)] + \
  [x.name for x in fields(CorrelatedMeasurements)] + \
  list(ALLOWED_GLOBALS.keys())

ALLOWED_NAMES = set([name for name in ALLOWED_NAMES if not name.startswith('_')])
