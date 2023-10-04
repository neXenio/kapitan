# Copyright 2019 The Kapitan Authors
# SPDX-FileCopyrightText: 2020 The Kapitan Authors <kapitan-admins@googlegroups.com>
#
# SPDX-License-Identifier: Apache-2.0

"hashicorp vault resource functions"

import logging
import os

import hvac

from kapitan.errors import KapitanError

logger = logging.getLogger(__name__)


class VaultError(KapitanError):
    """Generic vault errors"""

    pass


class VaultClient(hvac.Client):
    """client connects to vault server and authenticates itself"""

    def __init__(self, vault_parameters):
        self.vault_parameters = vault_parameters
        client_parameters = get_env(vault_parameters)
        super().__init__(**client_parameters)

        self.authenticate()

    def get_auth_token(self):
        """
        get token either from environment or from file
        """
        auth_type = self.vault_parameters["auth"]
        token = ""

        if auth_type in ["token", "github"]:
            token = os.getenv("VAULT_TOKEN")
            if not token:
                token_file = os.path.join(os.path.expanduser("~"), ".vault-token")
                token = self.read_token_from_file(token_file)

        return token

    def read_token_from_file(self, token_file):
        try:
            with open(token_file, "r") as fp:
                token = fp.read()
        except IOError:
            raise VaultError("Cannot read file {}".format(token_file))

        if not token or len(token) == 0:
            raise VaultError("{} is empty".format(token_file))

        # clean up token of unwanted line endings
        token = token.replace("\n", "")
        token = token.replace("\r", "")

        return token

    def authenticate(self):
        # different login method based on authentication type
        auth_type = self.vault_parameters["auth"]

        token = self.get_auth_token()
        username = os.getenv("VAULT_USERNAME")
        password = os.getenv("VAULT_PASSWORD")

        # token
        if auth_type == "token":
            if token:
                self.token = token
            else:
                raise VaultError(
                    "token authentication failed: VAULT_TOKEN is empty and '~/.vaulttoken not found"
                )
        # github
        elif auth_type == "github":
            if token:
                self.auth.github.login = token
            else:
                raise VaultError(
                    "token authentication failed: VAULT_TOKEN is empty and '~/.vaulttoken not found"
                )
        # ldap
        elif auth_type == "ldap":
            if username and password:
                self.auth.ldap.login(username=username, password=password)
            else:
                raise VaultError("ldap authentication failed: VAULT_USERNAME or VAULT_PASSWORD is empty")
        # userpass
        elif auth_type == "userpass":
            if username and password:
                self.auth.userpass.login(username=username, password=password)
            else:
                raise VaultError("userpass authentication failed: VAULT_USERNAME or VAULT_PASSWORD is empty")
        # approle
        elif auth_type == "approle":
            role_id = os.getenv("VAULT_ROLE_ID")
            secret_id = os.getenv("VAULT_SECRET_ID")
            if role_id and secret_id:
                self.auth.approle.login(role_id, secret_id=secret_id)
            else:
                raise VaultError("approle authentication failed: VAULT_ROLE_ID or VAULT_SECRET_ID is empty")
        else:
            raise VaultError(f"Authentication type '{auth_type}' not supported")

        if not self.is_authenticated():
            self.adapter.close()
            raise VaultError("Vault Authentication Error, Environment Variables defined?")


def get_env(vault_parameters):
    """
    The following variables need to be exported to the environment or defined in inventory.
        * VAULT_ADDR: url for vault
        * VAULT_SKIP_VERIFY: if set, do not verify presented TLS certificate before communicating with Vault server.
        * VAULT_CLIENT_KEY: path to an unencrypted PEM-encoded private key matching the client certificate
        * VAULT_CLIENT_CERT: path to a PEM-encoded client certificate for TLS authentication to the Vault server
        * VAULT_CACERT: path to a PEM-encoded CA cert file to use to verify the Vault server TLS certificate
        * VAULT_CAPATH: path to a directory of PEM-encoded CA cert files to verify the Vault server TLS certificate
        * VAULT_NAMESPACE: specify the Vault Namespace, if you have one
    """
    client_parameters = {}

    # fetch missing values from env
    variables = ["ADDR", "NAMESPACE", "SKIP_VERIFY", "CACERT", "CAPATH", "CLIENT_KEY", "CLIENT_CERT"]
    for var in variables:
        var = "VAULT_" + var
        if vault_parameters.get(var) is None and os.getenv(var) is not None:
            vault_parameters[var] = os.getenv(var)

    # set vault adress
    vault_address = vault_parameters.get("VAULT_ADDR")
    if not vault_address:
        raise VaultError("VAULT_ADDR has to be specified in inventory or env")
    else:
        client_parameters["url"] = vault_address

    # set vault namespace
    vault_namespace = vault_parameters.get("VAULT_NAMESPACE")
    if vault_namespace:
        client_parameters["namespace"] = vault_namespace

    # set ca cert/path or skip verification
    skip_verify = not (str(vault_parameters.get("VAULT_SKIP_VERIFY", False)).lower() == "false")
    if skip_verify:
        # TODO: surpress ssl warning
        client_parameters["verify"] = False
    else:
        cert = vault_parameters.get("VAULT_CACERT")
        cert_path = vault_parameters.get("VAULT_CAPATH")
        if cert and os.path.isfile(cert):
            client_parameters["verify"] = cert
        elif cert_path and os.path.isdir(cert_path):
            client_parameters["verify"] = cert_path
        else:
            raise VaultError("Neither VAULT_CACERT nor VAULT_CAPATH specified or exist")

    # set client cert for tls authentication
    client_key = vault_parameters.get("VAULT_CLIENT_KEY")
    client_cert = vault_parameters.get("VAULT_CLIENT_CERT")
    if client_key and client_cert:
        client_parameters["cert"] = (client_cert, client_key)

    return client_parameters
