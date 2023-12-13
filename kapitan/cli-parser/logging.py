import argparse

def build_logging_parser():
    parser = argparse.ArgumentParser(prog=PROJECT_NAME, description=DESCRIPTION)
    parser.add_argument("--version", action="version", version=VERSION)
    subparser = parser.add_subparsers(help="commands", dest="subparser_name")

    # setup parent parser to use log arguments in every subparser
    logger_parser = argparse.ArgumentParser(add_help=False)
    logger_group = logger_parser.add_argument_group("logging")
    logger_group.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        default=from_dot_kapitan("logging", "quiet", False),
        help="set the output level to 'quiet' and only see critical errors",
    )
    logger_group.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        default=from_dot_kapitan("logging", "verbose", False),
        help="set the output level to 'verbose' and see debug information",
    )
    logger_group.add_argument(
        "--no-color",
        action="store_true",
        default=from_dot_kapitan("logging", "no_color", False),
        help="disable the coloring in the debug output",
    )
    logger_group.add_argument(
        "--log-file",
        type=str,
        metavar="FILENAME",
        action="store",
        default=from_dot_kapitan("logging", "log_file", None),
        help="specify a name/path if you want to have your debug output in a file",
    )
