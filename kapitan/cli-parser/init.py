init_parser = subparser.add_parser(
        "init",
        help="initialize a directory with the recommended kapitan project skeleton.",
        parents=[logger_parser],
    )
    init_parser.set_defaults(func=initialise_skeleton, name="init")

    init_parser.add_argument(
        "--directory",
        default=from_dot_kapitan("init", "directory", "."),
        help="set path, in which to generate the project skeleton,"
        'assumes directory already exists. default is "./"',
    )