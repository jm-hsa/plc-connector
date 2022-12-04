import logging
import time

logger = logging.getLogger(__name__)

class PrintStats:
  def __init__(self, parent):
    self.startTime = time.monotonic()

  def execute(self, values):
    counts = {}
    dt = time.monotonic() - self.startTime
    self.startTime = time.monotonic()
    text = ""
    warn = False
    for meas in values:
      id = "{} {}".format(meas.series, meas.source)
      if id in counts:
        counts[id] += 1
      else:
        counts[id] = 1
    if counts:
      ids = list(counts.keys())
      ids.sort()
      for id in ids:
        text += "{}: {:4d} in {:.03f}s, {:.1f}/s    ".format(id, counts[id], dt, counts[id] / dt)
    else:
      text = "0 Messungen in {:.03f}s               ".format(dt)
      warn = True

    if warn:
      logger.warning(text)
    else:
      logger.info(text)
    return values

class Warning:
  def __init__(self, parent):
    pass

  def execute(self, values):
    for meas in values:
      logger.warning(str(meas))
      yield meas