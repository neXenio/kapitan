validate_parser = subparser.add_parser(
        "validate",
        aliases=["v"],
        help="validates the compile output against schemas as specified in inventory",
        parents=[logger_parser],
    )
    validate_parser.set_defaults(func=schema_validate_compiled, name="validate")

    validate_parser.add_argument(
        "--compiled-path",
        default=from_dot_kapitan("compile", "compiled-path", "./compiled"),
        help='set compiled path, default is "./compiled',
    )
    validate_parser.add_argument(
        "--inventory-path",
        default=from_dot_kapitan("compile", "inventory-path", "./inventory"),
        help='set inventory path, default is "./inventory"',
    )
    validate_parser.add_argument(
        "--targets",
        "-t",
        help="targets to validate, default is all",
        type=str,
        nargs="+",
        default=from_dot_kapitan("compile", "targets", []),
        metavar="TARGET",
    ),
    validate_parser.add_argument(
        "--schemas-path",
        default=from_dot_kapitan("validate", "schemas-path", "./schemas"),
        help='set schema cache path, default is "./schemas"',
    )
    validate_parser.add_argument(
        "--parallelism",
        "-p",
        type=int,
        default=from_dot_kapitan("validate", "parallelism", 4),
        metavar="INT",
        help="Number of concurrent validate processes, default is 4",
    )
