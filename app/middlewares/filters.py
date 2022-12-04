import logging
from .common import MatchSeries, ALLOWED_NAMES, ALLOWED_GLOBALS

logger = logging.getLogger(__name__)
"""
This middleware filters the measurements by series and yields if any given field matches.
"""
class MatchAny(MatchSeries):
  def __init__(self, parent, series, **kwargs) -> None:
    super().__init__(series)
    self._fields = kwargs

  def execute(self, values):
    for measurement in values:
      dataset = self.get_series(measurement)

      if not dataset:
        continue
      
      if not self._fields:
        yield measurement
        continue

      # check if any field matches
      for field, value in self._fields.items():
        v = getattr(dataset, field, None)
        if v == value or (isinstance(v, tuple) and value in v):
          yield measurement
          break
      
"""
This middleware filters the measurements by series and yields if all given fields match.
"""
class MatchAll(MatchSeries):
  def __init__(self, parent, series, **kwargs) -> None:
    super().__init__(series)
    self._fields = kwargs

  def execute(self, values):
    for measurement in values:
      dataset = self.get_series(measurement)
      if not dataset:
        continue

      # check if all fields match
      success = True
      for field, value in self._fields.items():
        v = getattr(dataset, field, None)
        if (not isinstance(v, tuple) and v != value) or (isinstance(v, tuple) and not all(x == value for x in v)):
          success = False
          break
      if success:
        yield measurement

class ComplexFilter():
  def __init__(self, parent, predicate) -> None:
    self._predicate = predicate
    self._compiled = compile(predicate, "<string>", "eval")
    # Validate allowed names
    for name in self._compiled.co_names:
        if name not in ALLOWED_NAMES:
            raise NameError(f"The use of '{name}' is not allowed in '{predicate}'")

  def execute(self, values):
    for measurement in values:
      try:
        if eval(self._compiled, {"__builtins__": ALLOWED_GLOBALS}, measurement.__dict__):
          yield measurement
      except Exception as e:
        logger.error(f"Error while evaluating predicate '{self._predicate}': {e}")