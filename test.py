#!/usr/bin/env python3

import argparse
import configparser

config = configparser.ConfigParser()
config.read('config3.ini')
try:
    defaults = config['default']
except KeyError:
    defaults = dict()

parser = argparse.ArgumentParser()
parser.add_argument('-a', dest='arg1')
parser.add_argument('-b', dest='arg2')
parser.add_argument('-c', dest='arg3')
args = vars(parser.parse_args())
print(args)
result = dict(defaults)
result.update({k: v for k, v in args.items() if v is not None})  # Update if v is not None
print(result)