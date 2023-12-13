from .compile import compile_parser
from kapitan.version import DESCRIPTION, PROJECT_NAME, VERSION
import argparse


def build_parser():
    
    parser = argparse.ArgumentParser(prog=PROJECT_NAME, description=DESCRIPTION)
    parser.add_argument("--version", action="version", version=VERSION)
    
    # add 
    logging_parser = parser.add_subparsers()
    
    
    
    command_parser = parser.add_subparsers(help="commands", dest="subparser_name")
    
    
    
    
    compile_parser = command_parser.add_parser(
        "compile", aliases=["c"], help="compile targets", parents=[logger_parser, inventory_backend_parser]
    )
    compile_parser.set_defaults(func=trigger_compile, name="compile")