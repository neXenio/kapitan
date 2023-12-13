inventory_backend_parser = argparse.ArgumentParser(add_help=False)
    inventory_backend_group = inventory_backend_parser.add_argument_group("inventory_backend")
    inventory_backend_group.add_argument(
        "--reclass",
        action="store_true",
        default=from_dot_kapitan("inventory_backend", "reclass", False),
        help="use reclass as inventory backend (default)",
    )
    inventory_backend_group.add_argument(
        "--omegaconf",
        "-o",
        action="store_true",
        default=from_dot_kapitan("inventory_backend", "omegaconf", False),
        help="use OmegaConf as inventory backend",
    )
    inventory_backend_group.add_argument(
        "--migrate",
        help="migrate inventory to specified backend",
        action="store_true",
        default=from_dot_kapitan("inventory_backend", "migrate", False),
    )
    
    
inventory_parser = subparser.add_parser(
        "inventory", aliases=["i"], help="show inventory", parents=[logger_parser, inventory_backend_parser]
    )
    inventory_parser.set_defaults(func=generate_inventory, name="inventory")

    inventory_parser.add_argument(
        "--target-name",
        "-t",
        default=from_dot_kapitan("inventory", "target-name", ""),
        help="set target name, default is all targets",
    )
    inventory_parser.add_argument(
        "--inventory-path",
        default=from_dot_kapitan("inventory", "inventory-path", "./inventory"),
        help='set inventory path, default is "./inventory"',
    )
    inventory_parser.add_argument(
        "--flat",
        "-F",
        help="flatten nested inventory variables",
        action="store_true",
        default=from_dot_kapitan("inventory", "flat", False),
    )
    inventory_parser.add_argument(
        "--pattern",
        "-p",
        default=from_dot_kapitan("inventory", "pattern", ""),
        help="filter pattern (e.g. parameters.mysql.storage_class, or storage_class,"
        + ' or storage_*), default is ""',
    )
    inventory_parser.add_argument(
        "--indent",
        "-i",
        type=int,
        default=from_dot_kapitan("inventory", "indent", 2),
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
        default=from_dot_kapitan("inventory", "multiline-string-style", "double-quotes"),
        help="set multiline string style to STYLE, default is 'double-quotes'",
    )