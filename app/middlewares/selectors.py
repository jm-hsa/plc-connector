import logging
import re
import dataclasses
from .common import ALLOWED_NAMES, ALLOWED_GLOBALS
from structures.common import BaseMeasurement

logger = logging.getLogger(__name__)

@dataclasses.dataclass(frozen=True)
class Selection(BaseMeasurement):
  value: str
  series: str

class ComplexSelector():
  def __init__(self, parent, selector) -> None:
    self._selector = selector
    self._compiled = compile(selector, "<string>", "eval")
    # Validate allowed names
    for name in self._compiled.co_names:
        if name not in ALLOWED_NAMES:
            raise NameError(f"The use of '{name}' is not allowed in '{selector}'")

  def execute(self, values):
    for measurement in values:
      try:
        value = eval(self._compiled, {"__builtins__": ALLOWED_GLOBALS}, measurement.__dict__)
        yield Selection(
          timestamp = measurement.timestamp,
          series = re.match(r"[\w_\.\-\(\)]+", self._selector).group(0),
          source = "selection",
          value=value
        )
      except Exception as e:
        logger.error(f"Error while evaluating selector '{self._selector}': {e}")