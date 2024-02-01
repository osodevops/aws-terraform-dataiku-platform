import grp
import json
import logging
import os
import re
import subprocess
from os.path import exists

import requests

logger = logging.getLogger(__name__)


class VaultException(Exception):
    def __init__(self, message, errors):
        super().__init__(message)
        self.errors = errors
        logging.critical(f"{message}, {errors}")


class Vault:
    role: str
    endpoint: str
    skip_tls: str
    path: str
    nonce: str
    nonce_path: str
    mock: bool
    mock_values: dict
    method: str
    token: str

    def __init__(self, role, endpoint, skip_tls, auth_path, os_nonce_path, mock_endpoint=False, auth_method="aws",
                 auth_token=""):
        self.role = role
        self.endpoint = endpoint
        self.skip_tls = ""
        if skip_tls:
            self.skip_tls = "-tls-skip-verify"
        self.auth_path = auth_path
        self.os_nonce_path = os_nonce_path
        self.mock_endpoint = mock_endpoint
        self.mock_values = {}
        self.auth_method = auth_method
        self.auth_token = auth_token

    def load_nonce(self):
        self.nonce = ""
        if exists(self.os_nonce_path):
            with open(self.os_nonce_path, 'r') as f:
                self.nonce = re.sub("\n", "", f.read())

    def save_nonce(self):
        with open(self.os_nonce_path, 'w') as f:
            f.write(self.nonce)
        os.chmod(self.os_nonce_path, 0o440)
        os.chown(self.os_nonce_path, 0, grp.getgrnam('dataiku').gr_gid)

    def login(self):
        if self.mock_endpoint:
            return

        token = self.auth_token
        if self.auth_method == "aws":
            self.load_nonce()
            nonce = ""
            if self.nonce:
                nonce = f"nonce={self.nonce}"

            pkcs7 = requests.get("http://169.254.169.254/latest/dynamic/instance-identity/pkcs7").text
            pkcs7 = re.sub("\n", "", pkcs7)

            try:
                raw_output = subprocess.run(
                    f"vault write -address={self.endpoint} {self.skip_tls} auth/{self.path}/login method=aws "
                    f"path={self.path} role={self.role} pkcs7={pkcs7} {nonce} -format=json", shell=True,
                    check=True, capture_output=True)
            except subprocess.CalledProcessError as err:
                raise VaultException(f"Error: Could not login to vault", err)
            output = json.loads(raw_output.stdout)

            if output['auth']['metadata'].get('nonce'):
                self.nonce = output['auth']['metadata'].get('nonce')
                self.save_nonce()

            token = output['auth']['client_token']

        try:
            raw_output = subprocess.run(
                f"vault login -address={self.endpoint} {self.skip_tls} -format=json {token}", shell=True,
                check=True, capture_output=True)
        except subprocess.CalledProcessError as err:
            raise VaultException(f"Error: Could not login to vault", err)

    def get_kv(self, k_path):
        if self.mock_endpoint:
            return self.mock_values[k_path]

        try:
            raw_output = subprocess.run(
                f"vault kv get -address={self.endpoint} {self.skip_tls} -format=json {k_path}", shell=True,
                check=True, capture_output=True)
        except subprocess.CalledProcessError as err:
            raise VaultException(f"Error: Could not login to vault", err)
        output = json.loads(raw_output.stdout)

        return output['data']['data']
