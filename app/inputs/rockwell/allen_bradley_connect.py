import logging

from pylogix import PLC
from datetime import datetime

from structures.plant import *
from structures.measurement import *
from inputs.common import Input

localtz = datetime.now().astimezone().tzinfo
logger = logging.getLogger(__name__)

class AllenBradleyCPU(Input):
 
  def __init__(self, host):
    super().__init__(self.read_handler)
    self.comm = PLC()
    self.comm.IPAddress = host
    self.interval = 0.02
    self.cpu_state_tags = {
      "name": "B1[0]",
      
    }
    self.measurement_tags = {
      "24V": "B200",
      "480V": "B201"
    }
    self.tags = list(self.cpu_state_tags.values()) + list(self.measurement_tags.values())
    
  def read_handler(self):
    timestamp = datetime.now(localtz)
    ret = self.comm.Read(self.tags)
    if ret[0].Status == "Success":
      cpu_values = {t: r.Value for t, r in zip(self.cpu_state_tags, ret)}
      self._q.put(CompactLogixState(timestamp, "AB", **cpu_values))
      
      offset = self.cpu_state_tags.values()
      ifm_values_count = 22
      data = [r.Value for r in ret[offset:offset+ifm_values_count]]
      channels = 16
      self._q.put(Measurement24v(timestamp, "AB", 
        current = tuple([x / 10 for x in data[0:channels]]),
        status = tuple([data[16] & (1 << i) > 0 for i in range(channels)]),
        overload = tuple([data[17] & (1 << i) > 0 for i in range(channels)]),
        short_circuit = tuple([data[18] & (1 << i) > 0 for i in range(channels)]),
        limit = tuple([data[19] & (1 << i) > 0 for i in range(channels)]),
        pushbutton = tuple([data[20] & (1 << i) > 0 for i in range(channels)]),
        voltage = data[22] / 100
      ))
      offset += ifm_values_count
      data = [r.Value for r in ret[offset:offset+9]]
      self._q.put(Measurement480v(timestamp, "AB", 
        voltage = tuple(data[0:3]),
        current = tuple(data[3:6]),
        phase = tuple(data[6:9])
      ))

    else:
      logger.error("CPU read: " + ret[0].Status)