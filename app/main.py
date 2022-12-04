#!/usr/bin/env python3

import time
import yaml
import argparse
import logging
from logging.config import dictConfig
from importlib import import_module

# get config file from arguments

parser = argparse.ArgumentParser(description='PLC Connector')
parser.add_argument('-c', '--config', type=str, default='config.yml', help='config file')
args = parser.parse_args()

# read config
config = yaml.safe_load(open(args.config, 'r'))

dictConfig(config['Logging'])
logger = logging.getLogger(__name__)

def createModules(configItems, type):
  for item in configItems:
    cls = next(iter(item))
    module = import_module(f"{type}s.{item[cls]}")
    if item.get('enabled') == False:
      continue
    params = item.copy()
    params.pop(cls, None)
    params.pop('enabled', None)
    params.pop('submodules', None)
    params.pop('enable_output', None)
    try:
      yield getattr(module, cls)(**params)
    except Exception as ex:
      logger.fatal(F"{type} {cls} couldn't be initialized.", exc_info=False)
      raise

# setup input modules
inputs = list(createModules(config['Inputs'], "input"))

# setup middlewares recursively
def createMiddlewares(configItems, parent = None):
  items = [dict(x, parent=parent) for x in configItems if x.get('enabled') != False]
  middlewares = list(createModules(items, "middleware"))
  for (item, middleware) in zip(items, middlewares):
    if 'submodules' in item:
      middleware.submodules = list(createMiddlewares(item['submodules'], middleware))
      middleware.enable_output = item.get('enable_output', False)
    else:
      middleware.enable_output = item.get('enable_output', True)

  return middlewares

middlewares = createMiddlewares(config['Middlewares'])

# setup output modules
outputs = list(createModules(config['Outputs'], "output"))


for source in inputs:
  source.start()

logger.debug("started sources")

def executeMiddleware(middleware, values):
  submodules = getattr(middleware, 'submodules', [])
  result = list(middleware.execute(values))
  if not submodules and middleware.enable_output:
    return result
  else:
    subResults = []
    for submodule in submodules:
      subResults += executeMiddleware(submodule, result)
    return subResults

while True:
  values = set()
  for input in inputs:
    values.update(input.read())

  # sort the set by timestamp and series
  values = sorted(values, key=lambda x: (x.timestamp, x.series))

  # execute middlewares recursively and collect results of leaf modules

  results = set()
  for middleware in middlewares:
    tmp = executeMiddleware(middleware, values)
    if tmp:
      results.update(tmp)
  if not middlewares:
    results = values

  # sort the set by timestamp and series
  results = sorted(results, key=lambda x: (x.timestamp, x.series))

  for output in outputs:
    output.write(results)
    
  time.sleep(1.9)
