import subprocess


class DataikuController:
    binary_path: str
    command: str
    su_user: str

    def __init__(self, dss_path="/data/dataiku/bin", su_user="dataiku"):
        self.binary_path = dss_path
        self.su_user = su_user

    def _get_command(self, binary, command):
        if self.su_user:
            return f"su - {self.su_user} -c '{self.binary_path}/{binary} {command}'"
        return f"{self.binary_path}/{binary} {command}"

    def stop_dss_service(self):
        try:
            dsscli_output = subprocess.run(
                self._get_command('dss', 'stop'), shell=True,
                check=True, capture_output=True)
        except subprocess.CalledProcessError as err:
            raise Exception(f"Error: Could not stop DSS service via dss: {err.output}")

    def start_dss_service(self):
        try:
            dsscli_output = subprocess.run(
                self._get_command('dss', 'start'), shell=True,
                check=True, capture_output=True)
        except subprocess.CalledProcessError as err:
            raise Exception(f"Error: Could not start DSS service via dss: {err.output}")

    def regenerate_config(self):
        try:
            dsscli_output = subprocess.run(
                self._get_command('dssadmin', 'regenerate-config'), shell=True,
                check=True, capture_output=True)
        except subprocess.CalledProcessError as err:
            raise Exception(f"Error: Could not start DSS service via dss: {err.output}")