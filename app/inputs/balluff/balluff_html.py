from datetime import datetime
import time
import requests, json
import re

from inputs.common import Input

class Balluff(Input):

  cpu_start_time = None
  cpu_last_time = None
  local_start_time = time.time()
  db = 1
  interval = 0.05
  url = "http://192.168.10.20/ports.jsn"
  port = 0

  def __init__(self):
    super().__init__(self.read_handler)

  def read_handler(self):
    try:
      req = requests.get(self.url)
    except requests.exceptions.ConnectionError:
      return

    timestamp = datetime.utcnow()
    response = json.loads(req.text)
    if not re.match("^DF210[01]$", response['ports'][self.port]['productId']):
      raise Exception("unsupported device " + response['ports'][self.port]['productId'])

    data = response['ports'][self.port]['processInputs'].split(" ")
    data = bytes([int(x, 16) for x in data])
    
    self.queue_ifm_from_bytes(timestamp, data)
      