import logging

from datetime import datetime
import struct

from snap7.client import Client
from snap7.exceptions import Snap7Exception
from snap7.types import Areas

from structures.plant import *
from inputs.common import Input

localtz = datetime.now().astimezone().tzinfo
logger = logging.getLogger(__name__)

class SiemensCPU(Input):

  interval = 0.05

  def __init__(self, address) -> None:
    super().__init__(self.read_handler)
    self.address = address
    self.cpu = Client()

  def start(self):
    try:
      self.cpu.connect(self.address, rack=0, slot=0)
    except Snap7Exception as ex:
      logger.exception(ex)
    super().start()

  def read_handler(self):
    timestamp = datetime.now(localtz)
    cpu_state = self.cpu.get_cpu_state() == "S7CpuStatusRun"

    if self.cpu.get_connected():
      try:
        status = self.cpu.read_area(area=Areas.DB, dbnumber=3, start=0, size=5)
        #inputs = self.cpu.read_area(area=Areas.PE, dbnumber=0, start=32, size=112-32)
      except Snap7Exception as ex:
        if "TCP" in str(ex):
          self.cpu.disconnect()
          return
        else:
          raise ex
    else:
      self.cpu.disconnect()
      self.cpu.connect(self.address, rack=0, slot=0)
      return

    hydraulics_powered = status[0] & 1 > 0

    data = struct.unpack(">BBBBB", status)
    #print(''.join(["{:02X}".format(x) for x in inputs]))

    # TODO: Parse data

    self._q.put(PlantState(timestamp, "S7", cpu_state, *data))

  def get_timestamp(self, cpu_time):
    if not self.cpu_start_time:
      self.synchronize()
    cpu_diff = cpu_time - self.cpu_start_time
    date = datetime.fromtimestamp(self.local_start_time + cpu_diff, localtz)
    return date

      