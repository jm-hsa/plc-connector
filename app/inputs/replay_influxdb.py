import logging, time
from datetime import datetime, timedelta
from influxdb_client import InfluxDBClient

from inputs.common import Input
from structures.measurement import Measurement24v, Measurement480v
from structures.plant import CompactLogixState, S7State

dataclasses = [
  Measurement24v,
  Measurement480v,
  S7State,
  CompactLogixState,
]

logger = logging.getLogger(__name__)

class Replay(Input):
  def __init__(self, url, token, org, bucket, start_time) -> None:
    super().__init__(self.read_handler)
    self.interval = 1.0
    self.client = InfluxDBClient(url, token, org=org)
    self.bucket = bucket

    self.query_api = self.client.query_api()
    self.current_time = datetime.strptime(start_time, "%d.%m.%Y %H:%M:%S %z")
    self.time_offset = datetime.now().astimezone() - self.current_time
  
  def read_handler(self):
    start = self.current_time
    end = start + timedelta(seconds=1)
    for result in self.query(start, end):
      self._q.put(result)
    self.current_time = end

  def query(self, start, stop):
    query = f'from(bucket:"{self.bucket}")\
      |> range(start: {start.isoformat()}, stop: {stop.isoformat()})\
      |> yield(name: "m")'
    result = self.query_api.query(query=query)
    results = []
    fields = {}
    old_dataclass = None
    for table in result:
      
      if table.records:
        record = table.records[0]
        for cls in dataclasses:
          if record.get_measurement() == cls.series:
            dataclass = cls
            break
      
      if old_dataclass != dataclass:
        results.extend(self.populate_dataclasses(old_dataclass, fields))
        fields = {}
        old_dataclass = dataclass

      for record in table.records:
        if not record.get_time() in fields:
          fields[record.get_time()] = {}
        field = fields[record.get_time()]
        if 'channel' in record.values:
          field[record.get_field()] = field[record.get_field()] + (record.get_value(), ) if record.get_field() in field else (record.get_value(), )
        else:
          field[record.get_field()] = record.get_value()
        field['source'] = record['source']

    results.extend(self.populate_dataclasses(dataclass, fields))
    return results

  def populate_dataclasses(self, dataclass, fields):
    for time, values in fields.items():
      yield dataclass(time + self.time_offset, **values)
