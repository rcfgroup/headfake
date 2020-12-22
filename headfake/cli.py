import argparse

from headfake import output, HeadFake
from headfake.util import class_tree_from_yaml_file, locate_file

class Command:
    """
    Command line script
    """

    @staticmethod
    def run(args=None):
        """
        entrypoint for command line script

        Returns:
            None
        """
        command = Command(args)
        command.execute()

    def __init__(self, args=None):
        """
        __init__ constructor.

        initializes ArgumentParser and parses arguments passed at the  command line.
        """

        parser = argparse.ArgumentParser(
            description="HEAlth Data Faker provides a command-line script to create mock data "\
                "files based on a YAML-based template file (see examples for example templates). "\
                "It use the Python faker package to generate names and contact details.")

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
            default=0
        )

        self.args = parser.parse_args(args)

    def execute(self):
        """
        Runs the app by loading the configuration and generating data

        Returns:
            None
        """

        headfake = HeadFake(self.args.template, self.args.seed)

        if self.args.output_file:
            outfile = output.FileOutput(self.args)
        else:
            outfile = output.StdoutOutput(self.args)

        outfile.write(headfake.generate(self.args.no_rows))

