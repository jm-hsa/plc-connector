
from datetime import timedelta
from dataclasses import dataclass, fields
from .common import MatchSeries, ALLOWED_NAMES, ALLOWED_GLOBALS

"""
This middleware aggregates fields over a specified timespan.
"""
class Aggregate(MatchSeries):
  def __init__(self, parent, series, timespan, avg=[], sum=[], last=[], first=[], min=[], max=[]) -> None:
    super().__init__(series)
    self._timespan = timedelta(seconds=timespan)
    self._avg = avg
    self._sum = sum
    self._last = last
    self._first = first
    self._min = min
    self._max = max
    self._trigger_time = None
    self._datasets = []

    labels = {f: 'avg' for f in self._avg}
    labels.update({f: 'sum' for f in self._sum})
    labels.update({f: 'last' for f in self._last})
    labels.update({f: 'first' for f in self._first})
    labels.update({f: 'min' for f in self._min})
    labels.update({f: 'max' for f in self._max})

    self._name = f"{series} ({self._timespan.total_seconds()}s) {', '.join(f'{v}({k})' for k, v in labels.items())}"

  def execute(self, values):
    hasTriggered = False
    for measurement in values:
      dataset = self.get_series(measurement)
      if not dataset:
        continue

      self._last_measurement = measurement
      
      # set trigger time if not set
      if self._trigger_time is None:
        self._trigger_time = dataset.timestamp + self._timespan
      
      # check if we need to trigger
      if dataset.timestamp >= self._trigger_time and self._datasets:
        hasTriggered = True
        yield self.set_series(self._last_measurement, self.trigger())

      self._datasets.append(dataset)
    # trigger if we haven't received any new data or the trigger time has passed
    if (not hasTriggered and 
        self._datasets and 
        self._trigger_time and
        ((values and values[-1].timestamp >= self._trigger_time) or not values)):
      yield self.set_series(self._last_measurement, self.trigger())


  def apply_function(self, func, fields: list):
    last = self._datasets[-1]
    for field in fields:
      if isinstance(getattr(last, field), tuple):
        n = range(len(getattr(last, field)))
        yield (field, tuple(func(getattr(x, field)[i] for x in self._datasets) for i in n))
      else:
        yield (field, func(getattr(x, field) for x in self._datasets))

  def trigger(self):
    last = self._datasets[-1]
    field_dict = last.__dict__.copy()
    field_dict['series'] = self._name
    field_dict['source'] = 'aggregation'

    # apply aggregation functions
    field_dict.update(self.apply_function(lambda v: sum(v) / len(self._datasets), self._avg))
    field_dict.update(self.apply_function(sum, self._sum))
    field_dict.update((f, getattr(self._datasets[-1], f, 0)) for f in self._last)
    field_dict.update((f, getattr(self._datasets[0], f, 0)) for f in self._first)
    field_dict.update(self.apply_function(min, self._min))
    field_dict.update(self.apply_function(max, self._max))

    self._trigger_time = None
    self._datasets = []
    return type(last)(**field_dict)
    

