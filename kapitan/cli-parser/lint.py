lint_parser = subparser.add_parser(
        "lint", aliases=["l"], help="linter for inventory and refs", parents=[logger_parser]
    )
    lint_parser.set_defaults(func=start_lint, name="lint")

    lint_parser.add_argument(
        "--fail-on-warning",
        default=from_dot_kapitan("lint", "fail-on-warning", False),
        action="store_true",
        help="exit with failure code if warnings exist, default is False",
    )
    lint_parser.add_argument(
        "--skip-class-checks",
        action="store_true",
        help="skip checking for unused classes, default is False",
        default=from_dot_kapitan("lint", "skip-class-checks", False),
    )
    lint_parser.add_argument(
        "--skip-yamllint",
        action="store_true",
        help="skip running yamllint on inventory, default is False",
        default=from_dot_kapitan("lint", "skip-yamllint", False),
    )
    lint_parser.add_argument(
        "--search-secrets",
        default=from_dot_kapitan("lint", "search-secrets", False),
        action="store_true",
        help="searches for plaintext secrets in inventory, default is False",
    )
    lint_parser.add_argument(
        "--refs-path",
        help='set refs path, default is "./refs"',
        default=from_dot_kapitan("lint", "refs-path", "./refs"),
    )
    lint_parser.add_argument(
        "--compiled-path",
        default=from_dot_kapitan("lint", "compiled-path", "./compiled"),
        help='set compiled path, default is "./compiled"',
    )
    lint_parser.add_argument(
        "--inventory-path",
        default=from_dot_kapitan("lint", "inventory-path", "./inventory"),
        help='set inventory path, default is "./inventory"',
    )
    lint_parser.add_argument(
        "--omegaconf",
        help="use omegaconf as inventory backend",
        action="store_true",
        default=from_dot_kapitan("inventory", "omegaconf", False),
    )