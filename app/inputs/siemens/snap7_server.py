import snap7
import logging
import struct
import re
from datetime import datetime, tzinfo

from inputs.common import Input

localtz = datetime.now().astimezone().tzinfo
logger = logging.getLogger(__name__)

class SiemensServer(Input):
  interval = 0.02

  time_offset = None

  def __init__(self, port = 102):
    super().__init__(self.read_handler)
    self.server = snap7.server.Server(True)
    size = 100
    self.DB1 = (snap7.types.wordlen_to_ctypes[snap7.types.WordLen.Byte.value] * size)()
    self.DB2 = (snap7.types.wordlen_to_ctypes[snap7.types.WordLen.Byte.value] * size)()
    self.server.register_area(snap7.types.srvAreaDB, 1, self.DB1)
    self.server.register_area(snap7.types.srvAreaDB, 2, self.DB2)
    self.server.start(port)

  def read_handler(self):
    event : snap7.types.SrvEvent
    while True:
      event = self.server.pick_event()
      if not event:
        break
      text = self.server.event_text(event)
      match = re.match("^(?P<datetime>\d+-\d+-\d+ \d+:\d+:\d+) \[(?P<host>[\w\.:]+)\] (?P<type>[\w ]+), Area : (?P<area>.+), Start : (?P<start>\d+), Size : (?P<size>\d+) --> (?P<response>.+)$", text)
      if not match:
        logger.warn(text)
        continue
      
      if match.group("type") != "Write request":
        logger.warn(text)
        continue
      
      if int(match.group("start")) + int(match.group("size")) <= 4:
        continue

      if match.group("area") == "DB1":
        raw = bytearray(self.DB1)
        timestamp = self.get_timestamp(raw[0:4])
        self.queue_ifm_from_bytes("S7", timestamp, raw[4:34])
      elif match.group("area") == "DB2":
        raw = bytearray(self.DB2)
        timestamp = self.get_timestamp(raw[0:4])
        self.queue_energy_meter_from_bytes("S7", timestamp, raw[4:40])

  def get_timestamp(self, raw):
    now = datetime.now(localtz)
    cpu_time = struct.unpack(">I", raw)[0] / 1000
    offset = now.timestamp() - cpu_time
    if self.time_offset:
      self.time_offset = self.time_offset * 0.999 + offset * 0.001
    else:
      self.time_offset = offset
    
    timestamp = datetime.fromtimestamp(self.time_offset + cpu_time, localtz)
    return timestamp
