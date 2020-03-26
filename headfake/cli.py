from headfake import output
from headfake.util import class_tree_from_yaml_file

def generate_from_args(options):
    class_tree = class_tree_from_yaml_file(options.template)

    output_file = options.output_file

    if output_file:
        outfile = output.FileOutput(options)
    else:
        outfile = output.StdoutOutput(options)

    outfile.write_fieldset(class_tree.get("fieldset"))