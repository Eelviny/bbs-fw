# Responsible for writing the C header file.

from math import floor
from pint.registry import Quantity


def convert_pint_units_config(item_key: str, item_quantity: Quantity):
    unit_suffixes = {
        "ampere": "amps",
        "centivolt": "cV",
        "degree_Celsius": "c",
        "inch": "inch",
        "kilometer / hour": "kph",
        "millimeter": "mm",
        "millisecond": "ms",
        "second": "s",
        "volt": "v",
    }
    unit_suffix = unit_suffixes.get(str(item_quantity.units))
    return f"{item_key}_{unit_suffix}", floor(item_quantity.magnitude)


class HeaderFile:
    def __init__(self, file_location):
        self.file = open(file_location, "w")
        self.write_line("#ifndef _FWCONFIG_H_")
        self.write_line("#define _FWCONFIG_H_", 1)
        self.write_line("")

    def write_line(self, line, indentation_level=0):
        self.file.write(f"{'  ' * indentation_level}{line}\n")

    def write_define(self, key: str, value):
        if value is not None:
            if isinstance(value, bool):
                value = int(value)
            if isinstance(value, Quantity):
                key, value = convert_pint_units_config(key, value)
            self.write_line(f"#define {key.upper()} {value}", 1)

    def close_file(self):
        self.write_line("")
        self.write_line("#endif")
        self.file.close()
