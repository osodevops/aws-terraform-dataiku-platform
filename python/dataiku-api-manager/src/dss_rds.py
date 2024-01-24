import psycopg2
import subprocess

from dataiku_controller import DataikuController


class Rds:
    rds_client: psycopg2.connect
    rds_database_name: str
    rds_username: str
    rds_password: str
    rds_endpoint: str
    rds_schema_name: str
    rds_port: str
    dataiku_dss: DataikuController

    def __init__(self, rds_database_name, rds_username, rds_password, rds_endpoint, rds_port, rds_schema_name, dataiku=DataikuController()):
        self.rds_database_name = rds_database_name
        self.rds_username = rds_username
        self.rds_password = rds_password
        self.rds_endpoint = rds_endpoint
        self.rds_schema_name = rds_schema_name
        self.rds_port = rds_port
        self.rds_client = None
        self.dataiku_dss = dataiku

    def _ensure_client(self):
        if self.rds_client is None:
            self.rds_client = psycopg2.connect(
                dbname=self.rds_database_name,
                user=self.rds_username,
                password=self.rds_password,
                host=self.rds_endpoint,
                port=self.rds_port)

    def _check_schema_exists(self, rds_schema_name):
        self._ensure_client()
        cursor = self.rds_client.cursor()
        cursor.execute(f"SELECT schema_name FROM information_schema.schemata where schema_name = '{rds_schema_name}'")
        result = cursor.fetchone()
        cursor.close()
        if result:
            return True
        return False

    def _destroy_schema(self, rds_schema_name):
        self._ensure_client()
        cursor = self.rds_client.cursor()
        cursor.execute(f"drop schema if exists {rds_schema_name} cascade")
        self.rds_client.commit()
        cursor.close()

    def _create_schema(self, rds_schema_name, rds_username):
        self._ensure_client()
        cursor = self.rds_client.cursor()
        cursor.execute(f"create schema {rds_schema_name} authorization {rds_username}")
        self.rds_client.commit()
        cursor.close()

    def _close_connection(self):
        self.rds_client.close()
        self.rds_client = None

    @staticmethod
    def _copy_to_external():
        try:
            dsscli_output = subprocess.run(
                "su - dataiku -c '/data/dataiku/bin/dssadmin copy-databases-to-external'", shell=True,
                check=True, capture_output=True)
            # Check return value
        except subprocess.CalledProcessError as err:
            raise Exception(f"Error: Could not complete migration operation via dss: {err.output}")

    def check_database_sync(self, force="false"):
        # Are disk and database in sync?
        # How do we verify this? Schema exists?
        if force == "true":
            return False

        if self._check_schema_exists(self.rds_schema_name):
            print(f"RDS database Schema {self.rds_schema_name} exists")
            return True
        print(f"RDS database Schema {self.rds_schema_name} does not exist")
        self._close_connection()
        return False

    def initialise_database(self):
        if self._check_schema_exists(self.rds_schema_name):
            print(f"Dropping current schema {self.rds_schema_name}")
            self._destroy_schema(self.rds_schema_name)

        print(f"Creating schema {self.rds_schema_name}")
        self._create_schema(self.rds_schema_name, self.rds_username)
        self._close_connection()

    def migrate_database(self):
        print("Stopping service for database configuration")
        self.dataiku_dss.stop_dss_service()
        print("Migrating database")
        self._copy_to_external()
        print("Starting service")
        self.dataiku_dss.start_dss_service()

        if not self.check_database_sync():
            raise Exception('Error: Failed to sync installation to RDS')
        print("Migration successful")

    def generate_dss_config(self):
        return {
            "connection": {
                "params": {
                    "port": int(self.rds_port),
                    "host": self.rds_endpoint,
                    "user": self.rds_username,
                    "password": self.rds_password,
                    "db": self.rds_database_name,
                },
                "type": "PostgreSQL"
            },
            "schema": self.rds_schema_name,
        }
