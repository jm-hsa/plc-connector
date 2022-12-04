import csv
import os
from datetime import datetime
import dataclasses
import zipfile
import logging

from structures.common import BaseMeasurement

logger = logging.getLogger(__name__)

class CSVStorage:
  files = {}

  def __init__(self, path) -> None:
    self.path = path
    self.zipname = os.path.join(self.path, F"logs_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.zip")
  
  def write(self, values: list):
    try:
      for meas in values:
        if not meas.series in self.files:
          self.files[meas.series] = CSVFile(self.path, meas.series, self.zipname)
        self.files[meas.series].write(meas)
    except Exception as ex:
      logger.exception("CSV write failed")

class CSVFile:
  file = None
  filename = None
  row_count = 0

  def __init__(self, path, series, zipname) -> None:
    self.path = path
    self.series = series
    if not os.path.exists(self.path):
      os.mkdir(self.path)
    self.zipname = zipname
    self.new_file()

  def new_file(self):

    if self.file:
      self.file.close()
      with zipfile.ZipFile(self.zipname, 'a', compression=zipfile.ZIP_BZIP2, compresslevel=9) as zf:
        zf.write(self.filename, os.path.basename(self.filename))
      os.remove(self.filename)
      
    self.filename = os.path.join(self.path, F"{self.series}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv")
    self.file = open(self.filename, "w", newline='')
    self.writer = csv.writer(self.file, delimiter=',')

  def write(self, meas):
    row = dataclass_to_dict(meas)
    if self.row_count == 0:
      self.writer.writerow(row)
    self.writer.writerow(row.values())
    self.row_count += 1

    if self.row_count % 1000 == 0:
      self.file.flush()

    if self.row_count > 50000:
      self.new_file()
      self.row_count = 0


def dataclass_to_dict(dc, prefix=""):
  ret = {}
  for field in dataclasses.fields(dc):
    value = getattr(dc, field.name)
    if type(value) is tuple:
      for i, v in enumerate(value):
        ret[F"{prefix}{field.name}_{i}"] = v
    elif isinstance(value, BaseMeasurement):
      ret.update(dataclass_to_dict(value, F"{prefix}{value.series}_"))
    else:
      ret[F"{prefix}{field.name}"] = value
  return ret