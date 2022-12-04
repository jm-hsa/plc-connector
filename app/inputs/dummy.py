import logging
import random
import math
from datetime import datetime, timedelta, time
from inputs.common import Input as Inp

from structures.measurement import Measurement24v, Measurement480v
from structures.plant import S7State, CompactLogixState

logger = logging.getLogger(__name__)
localtz = datetime.now().astimezone().tzinfo

def f():
  return random.random()

def b():
  return random.choice([True, False])

def i(count=100):
  return random.randint(0, count-1)

class Input(Inp):
  def __init__(self, message) -> None:
    super().__init__(self.read_handler)
    logger.debug(message)
    self.interval = 0.01
  
  def read_handler(self):
    current = datetime.now()
    current_td = timedelta(
      hours = current.hour, 
      minutes = current.minute, 
      seconds = current.second, 
      microseconds = current.microsecond)

    # discretize to specified resolution
    to_sec = timedelta(seconds = round(current_td.total_seconds(), max(0, int(-math.log10(self.interval)))))
    timestamp = (datetime.combine(current, time(0)) + to_sec).astimezone(localtz)

    self._q.put(Measurement24v(
      timestamp - timedelta(seconds=0.05), 
      "dummy24v", 
      (f(), f(), f(), f(), f(), f(), f(), f(), f(), f(), f(), f(), f(), f(), f(), f()),
      (b(), b(), b(), b(), b(), b(), b(), b(), b(), b(), b(), b(), b(), b(), b(), b()),
      (b(), b(), b(), b(), b(), b(), b(), b(), b(), b(), b(), b(), b(), b(), b(), b()),
      (b(), b(), b(), b(), b(), b(), b(), b(), b(), b(), b(), b(), b(), b(), b(), b()),
      (b(), b(), b(), b(), b(), b(), b(), b(), b(), b(), b(), b(), b(), b(), b(), b()),
      (b(), b(), b(), b(), b(), b(), b(), b(), b(), b(), b(), b(), b(), b(), b(), b()),
      f() + 23.5
    ))
    self._q.put(Measurement480v(
      timestamp - timedelta(seconds=0.03),
      "dummy480v",
      (f()+230, f()+230, f()+230),
      (f(), f(), f()),
      (i(360), i(360), i(360))
    ))
    self._q.put(CompactLogixState(
      timestamp,
      "dummyAB",
      i(2), i(2), i(2), i(2), i(2), i(2), i(2), i(2), i(2), i(2), 
      i(2), i(2), i(2), i(2), i(2), i(2), i(2), i(2), i(2), i(2), 
      i(2), i(2), i(2), i(2), i(2), i(2), i(2), i(2), i(2), i(2), 
      i(2), i(2), i(2), i(2), i(2), i(2), i(2), i(2), i(2), i(2), 
      i(2), i(2), i(2), i(2), i(2), i(2), i(2), i(2), i(2), i(2), 
      i(2), i(2), i(2), i(2), i(2), i(2), i(2), i(2), i(2), i(2), 
      i(2), i(2)
    ))