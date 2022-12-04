import logging
import datetime
import json
from dataclasses import asdict

logger = logging.getLogger(__name__)

class DateTimeEncoder(json.JSONEncoder):
  def default(self, z):
    if isinstance(z, datetime.datetime):
      return z.isoformat()
    else:
      return super().default(z)

class JSONOutput:
  
  def write(self, values: set):
    for measurement in values:
      d = asdict(measurement)
      print(json.dumps(d, cls=DateTimeEncoder))