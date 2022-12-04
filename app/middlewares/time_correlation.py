import logging
from datetime import timedelta

from structures.correlated import CorrelatedMeasurements

logger = logging.getLogger(__name__)

class TimeCorrelation:
  def __init__(self, parent):
    self.state = {}
    self.timestamp = None
    self.old_values = []

  def execute(self, values: list):
    # combine new values with old values and sort them by timestamp and series
    values = sorted(self.old_values + values, key=lambda x: (x.timestamp, x.series))

    results = []
    # iterate over old values
    for i, measurement in enumerate(values[:len(self.old_values)]):
      self.state[type(measurement).__name__] = measurement

      if self.timestamp and self.timestamp > measurement.timestamp:
        logger.error(f"Timestamps are not in order: {measurement.series} is {self.timestamp - measurement.timestamp} to late")
      
      if len(values) > i+1 and values[i+1].timestamp == measurement.timestamp:
        continue

      self.timestamp = measurement.timestamp
      results.append(CorrelatedMeasurements(
        timestamp = measurement.timestamp,
        source = ','.join([x.source for x in self.state.values()]),
        measurement_24v = self.state.get("Measurement24v", None),
        measurement_480v = self.state.get("Measurement480v", None),
        measurement_plant = self.state.get("CompactLogixState", None) or self.state.get("S7State", None)
      ))

    # store new values for next iteration
    self.old_values = values[len(self.old_values):]
    return results