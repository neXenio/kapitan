#!/usr/bin/env python3

# Copyright 2019 The Kapitan Authors
# SPDX-FileCopyrightText: 2020 The Kapitan Authors <kapitan-admins@googlegroups.com>
#
# SPDX-License-Identifier: Apache-2.0

"command line module"

from __future__ import print_function

import argparse
import json
import logging
import multiprocessing
import os
import sys

import yaml

from kapitan import cached, defaults, setup_logging
from kapitan.initialiser import initialise_skeleton
from kapitan.inputs.jsonnet import jsonnet_file
from kapitan.lint import start_lint
from kapitan.refs.base import RefController, Revealer
from kapitan.refs.cmd_parser import handle_refs_command
from kapitan.resources import generate_inventory, resource_callbacks, search_imports
from kapitan.targets import compile_targets, schema_validate_compiled
from kapitan.utils import check_version, from_dot_kapitan, searchvar
from kapitan.version import DESCRIPTION, PROJECT_NAME, VERSION


def trigger_eval(args):
    file_path = args.jsonnet_file
    search_paths = [os.path.abspath(path) for path in args.search_paths]
    ext_vars = {}
    if args.vars:
        ext_vars = dict(var.split("=") for var in args.vars)
    json_output = None

    def _search_imports(cwd, imp):
        return search_imports(cwd, imp, search_paths)

    json_output = jsonnet_file(
        file_path,
        import_callback=_search_imports,
        native_callbacks=resource_callbacks(search_paths),
        ext_vars=ext_vars,
    )
    if args.output == "yaml":
        json_obj = json.loads(json_output)
        yaml.safe_dump(json_obj, sys.stdout, default_flow_style=False)
    elif json_output:
        print(json_output)


def trigger_compile(args):
    search_paths = [os.path.abspath(path) for path in args.search_paths]

    if not args.ignore_version_check:
        check_version()

    ref_controller = RefController(args.refs_path, embed_refs=args.embed_refs)
    # cache controller for use in reveal_maybe jinja2 filter
    cached.ref_controller_obj = ref_controller
    cached.revealer_obj = Revealer(ref_controller)

    compile_targets(
        args.inventory_path,
        search_paths,
        args.output_path,
        args.parallelism,
        args.targets,
        args.labels,
        ref_controller,
        schemas_path=args.schemas_path,
        jinja2_filters=args.jinja2_filters,
        verbose=hasattr(args, "verbose") and args.verbose,
        use_go_jsonnet=args.use_go_jsonnet,
        helm_refs=args.helm_refs,
        helm_refs_base64=args.helm_refs_base64,
        compose_node_name=args.compose_node_name,
    )


def build_parser():
    parser = argparse.ArgumentParser(prog=PROJECT_NAME, description=DESCRIPTION)
    parser.add_argument("--version", action="version", version=VERSION)
    subparser = parser.add_subparsers(help="commands", dest="subparser_name")


    compile_selector_parser = compile_parser.add_mutually_exclusive_group()
    compile_selector_parser.add_argument(
        "--targets",
        "-t",
        help="targets to compile, default is all",
        type=str,
        nargs="+",
        default=from_dot_kapitan("compile", "targets", []),
        metavar="TARGET",
    )
    compile_selector_parser.add_argument(
        "--labels",
        "-l",
        help="compile targets matching the labels, default is all",
        type=str,
        nargs="*",
        default=from_dot_kapitan("compile", "labels", []),
        metavar="key=value",
    )

    return parser


def main():
    """main function for command line usage"""
    try:
        multiprocessing.set_start_method("spawn")
    # main() is explicitly multiple times in tests
    # and will raise RuntimeError
    except RuntimeError:
        pass

    parser = build_parser()
    args = parser.parse_args()

    if getattr(args, "func", None) == generate_inventory and args.pattern and args.target_name == "":
        parser.error("--pattern requires --target_name")

    try:
        cmd = sys.argv[1]
    except IndexError:
        parser.print_help()
        sys.exit(1)

    # cache args where key is subcommand
    assert "name" in args, "All cli commands must have provided default name"
    cached.args[args.name] = args
    cached.args["all"] = args

    logging.debug(f"Running with args: {vars(args)}")

    # call chosen command
    args.func(args)

    return 0
