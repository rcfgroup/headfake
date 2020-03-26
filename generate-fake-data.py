# this is a simple command line script which creates  script will generate mock data
import sys

from headfake.cli import generate_from_args
import argparse

parser = argparse.ArgumentParser(description='HEAlth Data Faker provides a command-line script to create mock data files based on a YAML-based template file (see examples for example templates). It use the Python faker package to generate names and contact details.')

parser.add_argument("template", type=str,
                 help="YAML-based template file describing structure of health data fields to generate")

parser.add_argument("-o", "--output-file",
                 help="Output data to file rather than STDOUT")

parser.add_argument("-n", "--no-rows", type=int,
                 help="Number of rows to generate", default=1000)

args = parser.parse_args()

generate_from_args(args)
