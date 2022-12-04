import logging

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import dataclasses

logger = logging.getLogger(__name__)

class InfluxDB:
  def __init__(self, url, token, org, bucket):
    self.client = InfluxDBClient(url, token, org=org)

    self.bucket = bucket

    self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
    self.query_api = self.client.query_api()

  def write(self, values):
    points = []
    for meas in values:
      p = Point(meas.series).time(meas.timestamp).tag("source", meas.source)
      for field in dataclasses.fields(meas):
        if not field.name in ["timestamp", "series", "source"]:
          value = getattr(meas, field.name)
          if type(value) is bool:
            p.field(field.name, int(value))
          elif not type(value) is tuple:
            p.field(field.name, value)
          else:
            for i, v in enumerate(value):
              pt = Point(meas.series).time(meas.timestamp).tag("source", meas.source).tag("channel", i)
              if type(v) is bool:
                pt.field(F"{field.name}", int(v))
              else:
                pt.field(F"{field.name}", v)
              points.append(pt)
      points.append(p)
    try:
      self.write_api.write(bucket=self.bucket, record=points)
    except Exception as ex:
      logger.exception("Influx DB write failed")
