"""Contains the Lite class"""
import os
import re
from pathlib import Path
from colorama import Fore
import inflect
from pylite import LiteConnection
from pylite.lite_exceptions import (
    EnvFileNotFoundError,
    DatabaseNotFoundError,
    DatabaseAlreadyExistsError,
)


class Lite:
    """Helper functions for other Lite classes.

    Raises:
        EnvFileNotFoundError: Environment ('.env') file not found in script directory
        DatabaseNotFoundError: Database not specified by environment file or variables.
    """

    DATABASE_CONNECTIONS = {}
    DEFAULT_CONNECTION = None
    DEBUG_MODE = False

    @staticmethod
    def set_debug_mode(debug_mode: bool = True):
        """Sets debug mode. If True, Lite will print debug messages.

        Args:
            debug_mode (bool, optional): Defaults to True.
        """
        Lite.DEBUG_MODE = debug_mode

    @staticmethod
    def get_env() -> dict:
        """Returns dict of values from .env file.

        Raises:
            EnvFileNotFoundError: Environment ('.env') file not found in script directory

        Returns:
            dict: Dictionary containing the key-value pairings from the .env file.
        """

        if not os.path.exists(".env"):
            raise EnvFileNotFoundError()

        with open(".env", encoding="utf-8") as env:
            env_dict = dict([line.split("=") for line in env])

        return env_dict

    @staticmethod
    def get_database_path() -> str:
        """Returns sqlite database filepath.

        Raises:
            DatabaseNotFoundError: Database not specified by environment file or variables.

        Returns:
            str: Database filepath
        """

        db_path = os.environ.get("DB_DATABASE")
        if db_path is not None:
            return db_path

        env = Lite.get_env()
        if "DB_DATABASE" in env:
            return env["DB_DATABASE"]
        raise DatabaseNotFoundError("")

    @staticmethod
    def create_database(database_path: str):
        """Creates an empty SQLite database.

        Args:
            database_path (str): Desired database location

        Raises:
            DatabaseAlreadyExistsError: Database already exists at given filepath.
        """

        # Raise error if database already exists
        if os.path.exists(database_path):
            raise DatabaseAlreadyExistsError(database_path)

        # Create database
        Path(database_path).touch()

    @staticmethod
    def connect(lite_connection: LiteConnection):
        """Connects to a database."""
        Lite.DEFAULT_CONNECTION = lite_connection

        if Lite.DEBUG_MODE:
            print(Fore.RED, "Declared default connection:", lite_connection, Fore.RESET)

    @staticmethod
    def disconnect():
        """Disconnects from the default connection."""
        if Lite.DEFAULT_CONNECTION is not None:
            Lite.DEFAULT_CONNECTION.close()
            Lite.DEFAULT_CONNECTION = None

        if Lite.DEBUG_MODE:
            print(Fore.RED, "Disconnected from default connection", Fore.RESET)

    @staticmethod
    def declare_connection(label: str, lite_connection: LiteConnection):
        """Declares a connection to a database."""
        Lite.DATABASE_CONNECTIONS[label] = lite_connection

    class HelperFunctions:
        """Helper functions for other Lite classes."""

        @staticmethod
        def pluralize_noun(noun: str) -> str:
            """Returns plural form of noun. Used for table name derivations.

            Args:
                noun (str): Singular noun

            Returns:
                str: Plural noun
            """
            p = inflect.engine()
            return p.plural(noun)
