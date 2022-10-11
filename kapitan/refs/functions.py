# Copyright 2019 The Kapitan Authors
# SPDX-FileCopyrightText: 2020 The Kapitan Authors <kapitan-admins@googlegroups.com>
#
# SPDX-License-Identifier: Apache-2.0

"reference functions"

import base64
import hashlib
import logging
import secrets  # python secrets module
import string
import re

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519, rsa
from kapitan.errors import RefError

logger = logging.getLogger(__name__)


def eval_func(func_name, ctx, *func_params):
    """calls specific function which generates the secret"""
    func_lookup = get_func_lookup()

    return func_lookup[func_name](ctx, *func_params)


def get_func_lookup():
    """returns the lookup-table for the generator functions"""
    return {
        "randomstr": randomstr,
        "sha256": sha256,
        "ed25519": ed25519_private_key,
        "rsa": rsa_private_key,
        "rsapublic": rsa_public_key,
        "publickey": public_key,
        "reveal": reveal,
        "randomint": random_int,
        "loweralpha": lower_alpha,
        "loweralphanum": lower_alpha_num,
        "upperalpha": upper_alpha,
        "upperalphanum": upper_alpha_num,
        "alphanumspec": alphanumspec,
    }


def randomstr(ctx, nbytes=""):
    """
    generates a URL-safe text string, containing nbytes random bytes
    sets it to ctx.data
    """
    if nbytes:
        nbytes = int(nbytes)
        # Generate twice the amount of bytes asked for
        # and then trim the string to nbytes length if it's longer
        ctx.data = secrets.token_urlsafe(2 * nbytes)[:nbytes]

    else:
        ctx.data = secrets.token_urlsafe()


def sha256(ctx, salt=""):
    """sets ctx.data to salted sha256 hexdigest for input_value"""
    if ctx.data:
        salted_input_value = salt + ":" + ctx.data
        ctx.data = hashlib.sha256(salted_input_value.encode()).hexdigest()
    else:
        raise RefError(
            "Ref error: eval_func: nothing to sha256 hash; try " "something like '|randomstr|sha256'"
        )


def ed25519_private_key(ctx):
    """sets ctx.data to a ed25519 private key"""

    key = ed25519.Ed25519PrivateKey.generate()

    ctx.data = str(
        key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ),
        "utf-8",
    )


def rsa_private_key(ctx, key_size="4096"):
    """sets ctx.data to a RSA private key of key_size, default 4096"""
    rsa_key_size = int(key_size)

    key = rsa.generate_private_key(public_exponent=65537, key_size=rsa_key_size, backend=default_backend())

    ctx.data = str(
        key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ),
        "utf-8",
    )


def rsa_public_key(ctx):
    """Derives RSA public key from revealed private key"""
    if not ctx.data:
        raise RefError(
            "Ref error: eval_func: RSA public key cannot be derived; try "
            "something like '|reveal:path/to/encrypted_private_key|rsapublic'"
        )

    public_key(ctx)


def public_key(ctx):
    """Derives RSA public key from revealed private key"""
    if not ctx.data:
        raise RefError(
            "Ref error: eval_func: public key cannot be derived; try "
            "something like '|reveal:path/to/encrypted_private_key|publickey'"
        )

    data_dec = ctx.data
    if ctx.ref_encoding == "base64":
        data_dec = base64.b64decode(data_dec).decode()

    private_key = serialization.load_pem_private_key(
        data_dec.encode(), password=None, backend=default_backend()
    )
    public_key = private_key.public_key()

    ctx.data = str(
        public_key.public_bytes(
            encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo
        ),
        "UTF-8",
    )


def reveal(ctx, secret_path):
    """
    decrypt and return data from secret_path
    """
    token_type_name = ctx.ref_controller.token_type_name(ctx.token)
    secret_tag = "?{{{}:{}}}".format(token_type_name, secret_path)
    try:
        ref_obj = ctx.ref_controller[secret_tag]
        ctx.ref_encoding = ref_obj.encoding
        ctx.data = ref_obj.reveal()
    except KeyError:
        raise RefError(
            f"|reveal function error: {secret_path} file in {ctx.token}|reveal:{secret_path} does not exist"
        )


def random_int(ctx, ndigits="16"):
    """generates a number, containing ndigits random digits"""
    pool = string.digits
    generic_alphanum(ctx, ndigits, pool)


def lower_alpha(ctx, nchars="8"):
    """generator function for lowercase letters (a-z)"""
    pool = string.ascii_lowercase
    generic_alphanum(ctx, nchars, pool)


def lower_alpha_num(ctx, nchars="8"):
    """generator function for lowercase letters and numbers (a-z and 0-9)"""
    pool = string.ascii_lowercase + string.digits
    generic_alphanum(ctx, nchars, pool)


def upper_alpha(ctx, nchars="8"):
    """generator function for uppercase letters (A-Z)"""
    pool = string.ascii_uppercase
    generic_alphanum(ctx, nchars, pool)


def upper_alpha_num(ctx, nchars="8"):
    """generator function for uppercase letters and numbers (A-Z and 0-9)"""
    pool = string.ascii_uppercase + string.digits
    generic_alphanum(ctx, nchars, pool)


def alphanumspec(ctx, nchars="8", special_chars=string.punctuation):
    """
    generator function for alphanumeric characters and given special characters
    usage: ?{base64:path/to/secret||alphanumspec:32:#./&}
    default is !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~
    NOTE: '|' and ':' are used for arg parsing and aren't allowed manually, in default they work
    """
    # make sure that each character is include only once or not at all
    special_chars = "".join(set(special_chars).intersection(string.punctuation))
    pool = string.ascii_letters + special_chars
    print(pool)
    generic_alphanum(ctx, nchars, pool)


def generic_alphanum(ctx, nchars, pool):
    """
    generates a DNS-compliant text string, containing nchars from pool
    default for nchars is 8 chars
    sets it to ctx.data
    """
    # check input
    try:
        nchars = int(nchars)
    except ValueError:
        raise RefError(f"Ref error: eval_func: {nchars} cannot be converted into integer.")

    # generate string based on given pool
    generated_str = "".join(secrets.choice(pool) for i in range(nchars))

    # set ctx.data to generated string
    ctx.data = generated_str
