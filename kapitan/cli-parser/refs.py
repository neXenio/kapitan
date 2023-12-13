refs_parser = subparser.add_parser(
        "refs", aliases=["r"], help="manage refs", parents=[logger_parser, inventory_backend_parser]
    )
    refs_parser.set_defaults(func=handle_refs_command, name="refs")

    refs_parser.add_argument(
        "--write",
        "-w",
        help="write ref token",
        metavar="TOKENNAME",
    )
    refs_parser.add_argument(
        "--update",
        help="update GPG recipients for ref token",
        metavar="TOKENNAME",
    )
    refs_parser.add_argument(
        "--update-targets",
        action="store_true",
        default=from_dot_kapitan("refs", "update-targets", False),
        help="update target secret refs",
    )
    refs_parser.add_argument(
        "--validate-targets",
        action="store_true",
        default=from_dot_kapitan("refs", "validate-targets", False),
        help="validate target secret refs",
    )
    refs_parser.add_argument(
        "--base64",
        "-b64",
        help="base64 encode file content",
        action="store_true",
        default=from_dot_kapitan("refs", "base64", False),
    )
    refs_parser.add_argument(
        "--binary",
        help="file content should be handled as binary data",
        action="store_true",
        default=from_dot_kapitan("refs", "binary", False),
    )
    refs_parser.add_argument(
        "--reveal",
        "-r",
        help="reveal refs",
        action="store_true",
        default=from_dot_kapitan("refs", "reveal", False),
    )
    refs_parser.add_argument(
        "--tag", help='specify ref tag to reveal, e.g. "?{gkms:my/ref:123456}" ', metavar="REFTAG"
    )
    refs_parser.add_argument(
        "--ref-file", "-rf", help='read ref file, set "-" for stdin', metavar="REFFILENAME"
    )
    refs_parser.add_argument(
        "--file", "-f", help='read file or directory, set "-" for stdin', metavar="FILENAME"
    )
    refs_parser.add_argument("--target-name", "-t", help="grab recipients from target name")
    refs_parser.add_argument(
        "--inventory-path",
        default=from_dot_kapitan("refs", "inventory-path", "./inventory"),
        help='set inventory path, default is "./inventory"',
    )
    refs_parser.add_argument(
        "--recipients",
        "-R",
        help="set GPG recipients",
        type=str,
        nargs="+",
        default=from_dot_kapitan("refs", "recipients", []),
        metavar="RECIPIENT",
    )
    refs_parser.add_argument(
        "--key", "-K", help="set KMS key", default=from_dot_kapitan("refs", "key", ""), metavar="KEY"
    )
    refs_parser.add_argument(
        "--vault-auth",
        help="set authentication type for vault secrets",
        default=from_dot_kapitan("refs", "vault-auth", ""),
        metavar="AUTH",
    )
    refs_parser.add_argument(
        "--vault-mount",
        help="set mount point for vault secrets, default is 'secret'",
        default=from_dot_kapitan("refs", "vault-mount", "secret"),
        metavar="MOUNT",
    )
    refs_parser.add_argument(
        "--vault-path",
        help="set path for vault secrets where the secret gets stored on vault, default is the secret_path",
        default=from_dot_kapitan("refs", "vault-path", ""),
        metavar="PATH",
    )
    refs_parser.add_argument(
        "--vault-key",
        help="set key for vault secrets",
        default=from_dot_kapitan("refs", "vault-key", ""),
        metavar="KEY",
    )
    refs_parser.add_argument(
        "--refs-path",
        help='set refs path, default is "./refs"',
        default=from_dot_kapitan("refs", "refs-path", "./refs"),
    )
    refs_parser.add_argument(
        "--yaml-multiline-string-style",
        "-L",
        type=str,
        choices=["literal", "folded", "double-quotes"],
        metavar="STYLE",
        action="store",
        default=from_dot_kapitan("refs", "yaml-multiline-string-style", "double-quotes"),
        help="set multiline string style to STYLE, default is 'double-quotes'",
    )