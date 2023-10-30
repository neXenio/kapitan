#!/usr/bin/env python3

# Copyright 2023 The Kapitan Authors
# SPDX-FileCopyrightText: 2023 The Kapitan Authors <kapitan-admins@googlegroups.com>
#
# SPDX-License-Identifier: Apache-2.0

import os
from argparse import ArgumentParser

import yaml

from kapitan_new.commands.compile import compile
from kapitan_new.version import DESCRIPTION, PROJECT_NAME, VERSION

# from kapitan_new.commands.inventory import inventory


def build_parser():
    # load .kapitan file
    kapitan_config = {}
    if os.path.isfile(".kapitan"):
        with open(".kapitan", "r") as f:
            kapitan_config = yaml.safe_load(f)

    # create general parser
    parser = ArgumentParser(prog=PROJECT_NAME, description=DESCRIPTION)
    parser.add_argument("-v", "--version", action="version", version=VERSION)
    subparser = parser.add_subparsers(help="commands", dest="subparser_name")

    # -----------------------------------------------
    # Logging parser
    # -----------------------------------------------
    logger_parser = ArgumentParser(add_help=False)
    logger_group = logger_parser.add_argument_group("logging")
    logger_level_group = logger_group.add_mutually_exclusive_group()
    logger_level_group.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        default=kapitan_config.get("quiet", False),
        help="set the output level to 'quiet' and only see critical errors",
    )
    logger_level_group.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        default=kapitan_config.get("verbose", False),
        help="set the output level to 'verbose' and see debug information",
    )
    logger_group.add_argument(
        "--no-color",
        action="store_true",
        default=kapitan_config.get("no_color", False),
        help="disable the coloring in the debug output",
    )
    # logger_group.add_argument(
    #     "--log-file",
    #     type=str,
    #     metavar="FILENAME",
    #     action="store",
    #     default=kapitan_config.get("logging", "log_file", None),
    #     help="specify a name/path if you want to have your debug output in a file",
    # )

    # -----------------------------------------------
    # Inventory backend parser
    # -----------------------------------------------
    inventory_backend_parser = ArgumentParser(add_help=False)
    inventory_backend_group = inventory_backend_parser.add_argument_group("inventory backend")
    inventory_backend_group = inventory_backend_group.add_mutually_exclusive_group()
    inventory_backend_group.add_argument(
        "--reclass",
        action="store_true",
        default=kapitan_config.get("reclass", False),
        help="use reclass as inventory backend (default)",
    )
    inventory_backend_group.add_argument(
        "--omegaconf",
        "-o",
        action="store_true",
        default=kapitan_config.get("omegaconf", False),
        help="use OmegaConf as inventory backend",
    )

    # -----------------------------------------------
    # Target selector parser
    # -----------------------------------------------
    target_selector_parser = ArgumentParser(add_help=False)
    target_selector_group = target_selector_parser.add_argument_group("target selector")
    target_selector_group = target_selector_group.add_mutually_exclusive_group()
    target_selector_group.add_argument(
        "--targets",
        "-t",
        help="targets to compile, default is all",
        type=str,
        nargs="+",
        default=kapitan_config.get("targets", []),
        metavar="TARGET",
    )
    target_selector_group.add_argument(
        "--labels",
        "-l",
        help="compile targets matching the labels, default is all",
        type=str,
        nargs="*",
        default=kapitan_config.get("labels", []),
        metavar="key=value",
    )

    # -----------------------------------------------
    # Compile parser
    # -----------------------------------------------
    compile_parser = subparser.add_parser(
        name="compile",
        aliases=["c"],
        help="compile targets",
        parents=[logger_parser, inventory_backend_parser, target_selector_parser],
    )
    compile_parser.set_defaults(func=compile)

    compile_parser.add_argument(
        "--search-paths",
        "-J",
        type=str,
        nargs="+",
        default=kapitan_config.get("search-paths", [".", "lib"]),
        metavar="JPATH",
        help='set search paths, default is ["."]',
    )
    compile_parser.add_argument(
        "--output-path",
        type=str,
        default=kapitan_config.get("output-path", "."),
        metavar="PATH",
        help='set output path, default is "."',
    )
    compile_parser.add_argument(
        "--fetch",
        help="fetch remote inventories and/or external dependencies",
        action="store_true",
        default=kapitan_config.get("fetch", False),
    )
    compile_parser.add_argument(
        "--force-fetch",
        help="overwrite existing inventory and/or dependency item",
        action="store_true",
        default=kapitan_config.get("force-fetch", False),
    )
    compile_parser.add_argument(
        "--parallelism",
        "-p",
        type=int,
        default=kapitan_config.get("parallelism", 4),
        metavar="INT",
        help="Number of concurrent compile processes, default is 4",
    )
    compile_parser.add_argument(
        "--indent",
        "-i",
        type=int,
        default=kapitan_config.get("indent", 2),
        metavar="INT",
        help="Indentation spaces for YAML/JSON, default is 2",
    )
    compile_parser.add_argument(
        "--refs-path",
        help='set refs path, default is "./refs"',
        default=kapitan_config.get("refs-path", "./refs"),
    )
    compile_parser.add_argument(
        "--reveal",
        help="reveal refs (warning: this will potentially write sensitive data)",
        action="store_true",
        default=kapitan_config.get("reveal", False),
    )
    compile_parser.add_argument(
        "--inventory-path",
        default=kapitan_config.get("inventory-path", "./inventory"),
        help='set inventory path, default is "./inventory"',
    )
    compile_parser.add_argument(
        "--compose-node-name",
        help="Create same subfolder structure from inventory/targets inside compiled folder",
        action="store_true",
        default=kapitan_config.get("compose-node-name", False),
    )

    # -----------------------------------------------
    # Inventory parser
    # -----------------------------------------------
    inventory_parser = subparser.add_parser(
        name="inventory",
        aliases=["i"],
        help="show inventory",
        parents=[logger_parser, inventory_backend_parser, target_selector_parser],
    )
    # inventory_parser.set_defaults(func=inventory)

    inventory_parser.add_argument(
        "--flat",
        "-F",
        help="flatten nested inventory variables",
        action="store_true",
        default=kapitan_config.get("flat", False),
    )
    inventory_parser.add_argument(
        "--indent",
        "-i",
        type=int,
        default=kapitan_config.get("indent", 2),
        metavar="INT",
        help="Indentation spaces for inventory output, default is 2",
    )
    inventory_parser.add_argument(
        "--multiline-string-style",
        "-L",
        type=str,
        choices=["literal", "folded", "double-quotes"],
        metavar="STYLE",
        action="store",
        default=kapitan_config.get("multiline-string-style", "double-quotes"),
        help="set multiline string style to STYLE, default is 'double-quotes'",
    )

    return parser
