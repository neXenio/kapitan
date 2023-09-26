# Copyright 2019 The Kapitan Authors
# SPDX-FileCopyrightText: 2020 The Kapitan Authors <kapitan-admins@googlegroups.com>
#
# SPDX-License-Identifier: Apache-2.0

"hashicorp vault resource functions"

import logging
import os
import shutil
import socket
from time import sleep

import docker
import hvac

from kapitan.errors import KapitanError

logger = logging.getLogger(__name__)


class VaultServerError(KapitanError):
    """Generic vaultserver errors"""

    pass


class VaultServer:
    """Opens a vault server in a container"""

    def __init__(self, ref_path, name=None):
        self.docker_client = docker.from_env()
        self.socket, self.port = self.find_free_port()
        self.container = self.setup_container(name)

        self.ref_path = ref_path
        self.vault_client = None

    def setup_container(self, name=None):
        env = {
            "VAULT_LOCAL_CONFIG": '{"backend": {"file": {"path": "/vault/file"}}, "listener":{"tcp":{"address":"0.0.0.0:8200","tls_disable":"true"}}}'
        }
        container = self.docker_client.containers.run(
            image="hashicorp/vault",
            cap_add=["IPC_LOCK"],
            ports={"8200/tcp": self.port},
            environment=env,
            detach=True,
            remove=True,
            command="server",
            name=name,
        )
        # make sure the container is up & running before testing
        while container.status != "running":
            sleep(1)
            container.reload()

        return container

    def find_free_port(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("", 0))
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        port = sock.getsockname()[1]
        return sock, port

    def setup_vault(self):
        token = self.initialize()
        self.enable_engine(token)
        self.set_vault_attributes()

    def initialize(self):
        # Initialize vault, unseal, mount secret engine & get token
        os.environ["VAULT_ADDR"] = f"http://127.0.0.1:{self.port}"
        self.vault_client = hvac.Client()
        initialized_client = self.vault_client.sys.initialize()
        self.vault_client.sys.submit_unseal_keys(initialized_client["keys"])
        token = initialized_client["root_token"]
        os.environ["VAULT_ROOT_TOKEN"] = token
        self.vault_client.adapter.close()
        return token

    def enable_engine(self, token):
        self.vault_client = hvac.Client(token=token)
        self.vault_client.sys.enable_secrets_engine(backend_type="kv-v2", path="secret")

    def get_policy(self):
        test_policy = """
            path "secret/*" {
            capabilities = ["read", "list", "create", "update"]
            }
        """
        return test_policy

    def set_vault_attributes(self):
        policy = "test_policy"
        test_policy = self.get_policy()
        self.vault_client.sys.create_or_update_policy(name=policy, policy=test_policy)
        os.environ["VAULT_USERNAME"] = "test_user"
        os.environ["VAULT_PASSWORD"] = "test_password"
        self.vault_client.sys.enable_auth_method("userpass")
        self.vault_client.auth.userpass.create_or_update_user(
            username="test_user", password="test_password", policies=[policy]
        )
        self.vault_client.sys.enable_auth_method("approle")
        self.vault_client.auth.approle.create_or_update_approle("test_role")
        os.environ["VAULT_ROLE_ID"] = self.vault_client.auth.approle.read_role_id("test_role")["data"][
            "role_id"
        ]
        os.environ["VAULT_SECRET_ID"] = self.vault_client.auth.approle.generate_secret_id("test_role")[
            "data"
        ]["secret_id"]
        os.environ["VAULT_TOKEN"] = self.vault_client.auth.token.create(policies=[policy], ttl="1h")["auth"][
            "client_token"
        ]

    def close_container(self):
        self.vault_client.adapter.close()

        self.container.stop()
        self.docker_client.close()

        shutil.rmtree(self.ref_path, ignore_errors=True)
        for i in ["ROOT_TOKEN", "TOKEN", "USERNAME", "PASSWORD", "ROLE_ID", "SECRET_ID"]:
            del os.environ["VAULT_" + i]


class VaultTransitServer(VaultServer):
    def enable_engine(self, token):
        self.vault_client = hvac.Client(token=token)
        self.vault_client.sys.enable_secrets_engine(backend_type="transit", path="transit")

    def get_policy(self):
        test_policy = """
        path "transit/encrypt/*" {
            capabilities = [ "create", "update" ]
        }
        path "transit/decrypt/*" {
            capabilities = [ "create", "update" ]
        }
        """
        return test_policy


# try:
#     server = VaultServer("", "test_vaultkv")
#     server.setup_vault()
#     for log in server.container.logs().decode().split("\n"):
#         print(log)
# except Exception as e:
#     print("logs:")
#     for log in server.container.logs().decode().split("\n"):
#         print(log)
#     raise e
# finally:
#     server.socket.close()
#     server.container.stop()
#     server.docker_client.close()

# coverage run --source=kapitan --omit="*reclass*" -m unittest discover
# coverage report --fail-under=65 -m


def main():
    try:
        docker_client = docker.from_env()
        env = {
            "VAULT_LOCAL_CONFIG": '{"ui": true, "backend": {"file": {"path": "/vault/file"}}, "listener":{"tcp":{"address":"0.0.0.0:8200","tls_disable":"true"}}}'
        }
        port = 8200
        # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        #     sock.bind(("", 0))
        #     sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #     port = sock.getsockname()[1]

        container = docker_client.containers.run(
            image="hashicorp/vault",
            cap_add=["IPC_LOCK"],
            ports={"8200": port},
            environment=env,
            detach=True,
            remove=True,
            command="server",
            name="test_vaultkv",
        )
        # make sure the container is up & running before testing
        while container.status != "running":
            sleep(2)
            container.reload()

        import requests
        r = requests.get("http://127.0.0.1:8200/")
        print("curl to localhost:", r.status_code)

    except Exception as e:
        raise e
    finally:
        container.stop()
        docker_client.close()


main()
