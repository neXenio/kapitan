from kapitan_new.cli import build_parser
from kapitan_new.logger import setup_global_logging

if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    logger = setup_global_logging(args.verbose, args.quiet, not args.no_color)
    logger.debug(f"Running with args: {vars(args)}")
    logger.warning("hey")
    args.func(args)
