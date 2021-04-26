from abc import ABC, abstractmethod

class Output(ABC):
    """
    Base output class.
    """

    @abstractmethod
    def write(self, dataframe):
        """
        Main method used to write the fieldset to the output.
        :param dataframe:
        :return:
        """
        pass


class FileOutput(Output):
    """
    Output generated mock data for a single fieldset to the tab-delimited text file specified in
    the options (output_file)
    """

    def __init__(self, options):
        """
        Setup output with appropriate options.
        :param options: Arguments dictionary
        """
        self.output_file = options.output_file

    @abstractmethod
    def write(self, dataframe):
        pass

class CsvFileOutput(Output):
    """
    Output generated mock data for a single fieldset to the tab-delimited text file specified in
    the options (output_file)
    """

    def __init__(self, options):
        """
        Setup output with appropriate options.
        :param options: Arguments dictionary
        """
        self.output_file = options.output_file

    def write(self, dataframe):
        dataframe.to_csv(self.output_file)


class JsonFileOutput(Output):
    """
    Output generated mock data for a single fieldset to the tab-delimited text file specified in
    the options (output_file)
    """

    def __init__(self, options):
        """
        Setup output with appropriate options.
        :param options: Arguments dictionary
        """
        self.output_file = options.output_file

    def write(self, dataframe):
        dataframe.to_json(self.output_file)


class StdoutOutput(FileOutput):
    """
    Output generated mock data for a single fieldset to the console/STDOUT
    """

    def write(self, dataframe):
        print(dataframe)


