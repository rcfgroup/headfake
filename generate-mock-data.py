# this script will generate mock data
import sys

from mockd.util import config_from_yaml_file
from mockd import output
import argparse

import csv

parser = argparse.ArgumentParser(description='Generate mock data')
parser.add_argument("config", type=str,
                 help="YAML-based config file describing mock data to generate")
parser.add_argument("-o", "--output-file",
                 help="Output data to file rather than STDOUT")

parser.add_argument("-n", "--no-rows", type=int,
                 help="Number of rows to generate", default=1000)


options = parser.parse_args()

conf = config_from_yaml_file(options.config)


no_rows = int(options.no_rows)

output_file = options.output_file

if output_file:
    outfile = output.FileOutput(options)
else:
    outfile = output.StdoutOutput(options)

outfile.write_fieldset(conf.get("fieldset"))