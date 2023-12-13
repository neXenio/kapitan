compile_parser = subparser.add_parser(
        "compile", aliases=["c"], help="compile targets", parents=[logger_parser, inventory_backend_parser]
    )
    compile_parser.set_defaults(func=trigger_compile, name="compile")

    compile_parser.add_argument(
        "--search-paths",
        "-J",
        type=str,
        nargs="+",
        default=from_dot_kapitan("compile", "search-paths", [".", "lib"]),
        metavar="JPATH",
        help='set search paths, default is ["."]',
    )
    compile_parser.add_argument(
        "--jinja2-filters",
        "-J2F",
        type=str,
        default=from_dot_kapitan("compile", "jinja2-filters", defaults.DEFAULT_JINJA2_FILTERS_PATH),
        metavar="FPATH",
        help="load custom jinja2 filters from any file, default is to put\
                                them inside lib/jinja2_filters.py",
    )
    compile_parser.add_argument(
        "--prune",
        help="prune jsonnet output",
        action="store_true",
        default=from_dot_kapitan("compile", "prune", False),
    )
    compile_parser.add_argument(
        "--output-path",
        type=str,
        default=from_dot_kapitan("compile", "output-path", "."),
        metavar="PATH",
        help='set output path, default is "."',
    )
    compile_parser.add_argument(
        "--fetch",
        help="fetch remote inventories and/or external dependencies",
        action="store_true",
        default=from_dot_kapitan("compile", "fetch", False),
    )
    compile_parser.add_argument(
        "--force-fetch",
        help="overwrite existing inventory and/or dependency item",
        action="store_true",
        default=from_dot_kapitan("compile", "force-fetch", False),
    )
    compile_parser.add_argument(
        "--validate",
        help="validate compile output against schemas as specified in inventory",
        action="store_true",
        default=from_dot_kapitan("compile", "validate", False),
    )
    compile_parser.add_argument(
        "--parallelism",
        "-p",
        type=int,
        default=from_dot_kapitan("compile", "parallelism", 4),
        metavar="INT",
        help="Number of concurrent compile processes, default is 4",
    )
    compile_parser.add_argument(
        "--indent",
        "-i",
        type=int,
        default=from_dot_kapitan("compile", "indent", 2),
        metavar="INT",
        help="Indentation spaces for YAML/JSON, default is 2",
    )
    compile_parser.add_argument(
        "--refs-path",
        help='set refs path, default is "./refs"',
        default=from_dot_kapitan("compile", "refs-path", "./refs"),
    )
    compile_parser.add_argument(
        "--reveal",
        help="reveal refs (warning: this will potentially write sensitive data)",
        action="store_true",
        default=from_dot_kapitan("compile", "reveal", False),
    )
    compile_parser.add_argument(
        "--embed-refs",
        help="embed ref contents",
        action="store_true",
        default=from_dot_kapitan("compile", "embed-refs", False),
    )
    compile_parser.add_argument(
        "--inventory-path",
        default=from_dot_kapitan("compile", "inventory-path", "./inventory"),
        help='set inventory path, default is "./inventory"',
    )
    compile_parser.add_argument(
        "--cache",
        "-c",
        help="enable compilation caching to .kapitan_cache\
        and dependency caching to .dependency_cache, default is False",
        action="store_true",
        default=from_dot_kapitan("compile", "cache", False),
    )
    compile_parser.add_argument(
        "--cache-paths",
        type=str,
        nargs="+",
        default=from_dot_kapitan("compile", "cache-paths", []),
        metavar="PATH",
        help="cache additional paths to .kapitan_cache, default is []",
    )
    compile_parser.add_argument(
        "--ignore-version-check",
        help="ignore the version from .kapitan",
        action="store_true",
        default=from_dot_kapitan("compile", "ignore-version-check", False),
    )
    compile_parser.add_argument(
        "--use-go-jsonnet",
        help="use go-jsonnet",
        action="store_true",
        default=from_dot_kapitan("compile", "use-go-jsonnet", False),
    )

    # compose-node-name should be used in conjunction with reclass
    # config "compose_node_name: true". This allows us to make the same subfolder
    # structure in the inventory folder inside the compiled folder
    # https://github.com/kapicorp/kapitan/issues/932
    compile_parser.add_argument(
        "--compose-node-name",
        help="Create same subfolder structure from inventory/targets inside compiled folder",
        action="store_true",
        default=from_dot_kapitan("compile", "compose-node-name", False),
    )

    compile_parser.add_argument(
        "--schemas-path",
        default=from_dot_kapitan("validate", "schemas-path", "./schemas"),
        help='set schema cache path, default is "./schemas"',
    )
    compile_parser.add_argument(
        "--yaml-multiline-string-style",
        "-L",
        type=str,
        choices=["literal", "folded", "double-quotes"],
        metavar="STYLE",
        action="store",
        default=from_dot_kapitan("compile", "yaml-multiline-string-style", "double-quotes"),
        help="set multiline string style to STYLE, default is 'double-quotes'",
    )
    compile_parser.add_argument(
        "--yaml-dump-null-as-empty",
        default=from_dot_kapitan("compile", "yaml-dump-null-as-empty", False),
        action="store_true",
        help="dumps all none-type entries as empty, default is dumping as 'null'",
    )
    compile_parser.add_argument(
        "--helm-refs",
        action="store_true",
        default=from_dot_kapitan("compile", "helm-secrets", False),
        help="enable kapitan secret engine on helm refs",
    )
    compile_parser.add_argument(
        "--helm-refs-base64",
        action="store_true",
        default=from_dot_kapitan("compile", "encode_base64", False),
        help="(helm-only) encode .data key with base64",
    )