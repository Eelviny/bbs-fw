import argparse

from pydantic import BaseModel
from pydantic_yaml import parse_yaml_raw_as
from validation import Config, PedalAssistLevels
from write_header import HeaderFile


def parse_yaml(file_path):
    with open(file_path, "r") as file:
        return parse_yaml_raw_as(Config, file)


def write_pas_levels(pas_levels: PedalAssistLevels, header_file: HeaderFile):
    for level_type, levels in pas_levels:
        for index, level in enumerate(levels.levels):
            # Header example ASSIST_LEVEL_STANDARD_0_FLAGS
            for level_key, level_value in level:
                header_file.write_define(
                    f"ASSIST_LEVEL_{level_type}_{index}_{level_key}",
                    level_value,
                )


def write_general(config: BaseModel, header_file: HeaderFile, prefix_category=""):
    for config_type, config_item in config:
        if isinstance(config_item, PedalAssistLevels):
            write_pas_levels(config_item, header_file)
        else:
            if isinstance(config_item, BaseModel):
                write_general(config_item, header_file, f"{config_type}_")
            else:
                header_file.write_define(
                    prefix_category + config_type,
                    config_item,
                )


def main():
    parser = argparse.ArgumentParser(
        prog="bbsxtra-programmer",
        description="A tool to compile firmware for the Bafang BBS02/BBSHD ebike motor",
    )
    _ = parser.add_argument("filename", help="Path to the yaml configuration file")
    args = parser.parse_args()
    config = parse_yaml(args.filename)

    header_file = HeaderFile("fwconfig.h")
    write_general(config, header_file)

    header_file.close_file()


if __name__ == "__main__":
    main()
