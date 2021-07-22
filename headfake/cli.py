"""
This package implements the command line interface for headfake
"""

import argparse

from headfake import output, HeadFake

import os

class Command:
    """
    Class for command line script
    """

    @staticmethod
    def run(args=None):
        """
        Entrypoint for command line script. this entry point is registered by setup.py when the
        package is installed.

        Returns:
            None
        """
        command = Command(args)
        command.execute()

    def __init__(self, args=None):
        """
        __init__ constructor.

        Initializes ArgumentParser and parses arguments passed at the command line.
        """

        parser = argparse.ArgumentParser(

            description="HEAlth Data Faker provides a command-line script to create mock data "
            "files based on a YAML-based template file (see examples/* for example "
            "templates). HeadFake uses the python package 'faker' to generate names and "
            "contact details.")

        parser.add_argument(
            "template",
            type=str,
            help="YAML-based template file describing structure of health data fields to generate"
        )

        parser.add_argument(
            "-o",
            "--output-file",
            help="Output data to file rather than STDOUT"
        )

        parser.add_argument(
            "-n",
            "--no-rows",
            type=int,
            help="Number of rows to generate",
            default=10
        )

        parser.add_argument(
            "-s",
            "--seed",
            type=int,
            help="Seed for the random data generator",
            required=False
        )

        self.args = parser.parse_args(args)

    def execute(self):
        """
        Runs the app by loading the configuration and generating data

        Returns:
            None
        """

        filename, file_ext = os.path.splitext(self.args.template)

        hf_load_fn = HeadFake.from_json if file_ext == "json" else HeadFake.from_yaml

        headfake = hf_load_fn(self.args.template, seed=self.args.seed)

        if self.args.output_file:
            outfile = output.CsvFileOutput(self.args)
        else:
            outfile = output.StdoutOutput(self.args)

        outfile.write(headfake.generate(self.args.no_rows))
