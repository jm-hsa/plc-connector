from threading import Thread
from queue import Queue
import time
import struct
import logging

from structures.measurement import *

logger = logging.getLogger(__name__)

class Input:
  _t = None
  _stop = False
  _q = Queue()

  interval = 1.0
  _read_cb = None

  def __init__(self, read_cb) -> None:
      self._read_cb = read_cb

  def start(self):
    if not self._t:
      self._stop = False
      self._t = Thread(target = self._main)
      self._t.setDaemon(True)
      self._t.start()

  def stop(self):
    if self._t:
      self._stop = True
      self._t.join()
      self._t = None

  def read(self):
    while not self._q.empty():
      yield self._q.get()

  def _main(self):
    start_time = time.monotonic()
    while not self._stop:
      try:
        self._read_cb()
      except Exception as e:
        logger.exception(F"An exception occured while reading from {type(self)}!")
        time.sleep(1)

      end_time = time.monotonic()
      remaining = self.interval + start_time - end_time
      if remaining > 0:
        start_time += self.interval
        time.sleep(remaining)
      else:
        start_time = end_time
        
  def queue_ifm_from_bytes(self, source, timestamp, raw, channels = 16):
    data = struct.unpack(">" + "B" * 16 + "HHHHHBxH", raw)
    current = tuple([x / 10 for x in data[0:channels]])
    status = tuple([data[16] & (1 << i) > 0 for i in range(channels)])
    overload = tuple([data[17] & (1 << i) > 0 for i in range(channels)])
    short_circuit = tuple([data[18] & (1 << i) > 0 for i in range(channels)])
    limit = tuple([data[19] & (1 << i) > 0 for i in range(channels)])
    pushbutton = tuple([data[20] & (1 << i) > 0 for i in range(channels)])
    voltage = data[22] / 100
    self._q.put(Measurement24v(timestamp, source, current, status, overload, short_circuit, limit, pushbutton, voltage))

  def queue_energy_meter_from_bytes(self, source, timestamp, raw):
    data = struct.unpack(">" + "f" * 9, raw)
    voltage = tuple(data[0:3])
    current = tuple(data[3:6])
    phase = tuple(data[6:9])
    self._q.put(Measurement480v(timestamp, source, voltage, current, phase))