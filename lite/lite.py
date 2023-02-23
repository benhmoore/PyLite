from pathlib import Path
from colorama import Fore, Back, Style

import os
from lite import *

class Lite:
    """Helper functions for other Lite classes.

    Raises:
        EnvFileNotFound: Environment ('.env') file not found in script directory
        DatabaseNotFoundError: Database not specified by environment file or variables.
    """

    DATABASE_CONNECTIONS = {}
    DEFAULT_CONNECTION = None

    @staticmethod
    def getEnv() -> dict:
        """Returns dict of values from .env file.

        Raises:
            EnvFileNotFound: Environment ('.env') file not found in script directory

        Returns:
            dict: Dictionary containing the key-value pairings from the .env file.
        """
        
        if not os.path.exists('.env'):
            raise EnvFileNotFound()

        env_dict = {}
        with open('.env') as env:
            for line in env:
                key, value = line.split('=')
                env_dict[key] = value
                
        return env_dict
    
    
    @staticmethod
    def getDatabasePath() -> str:
        """Returns sqlite database filepath.

        Raises:
            DatabaseNotFoundError: Database not specified by environment file or variables.

        Returns:
            str: Database filepath
        """

        db_path = os.environ.get('DB_DATABASE')
        if db_path is not None:
            return db_path
            
        env = Lite.getEnv()
        if 'DB_DATABASE' in env:
            return env['DB_DATABASE']
        else:
            raise DatabaseNotFoundError('')


    @staticmethod
    def createDatabase(database_path:str):
        """Creates an empty SQLite database.

        Args:
            database_path (str): Desired database location

        Raises:
            DatabaseAlreadyExists: Database already exists at given filepath.
        """

        # Raise error if database already exists
        if os.path.exists(database_path): raise DatabaseAlreadyExists(database_path)

        # Create database
        Path(database_path).touch()

    @staticmethod
    def connect(lite_connection:LiteConnection):
        Lite.DEFAULT_CONNECTION = lite_connection
        print(Fore.RED, "Declared default connection:", lite_connection, Fore.RESET)

    @staticmethod
    def disconnect():
        Lite.DEFAULT_CONNECTION = None
        print(Fore.RED, "Disconnected from default connection", Fore.RESET)

    @staticmethod
    def declareConnection(label:str, lite_connection:LiteConnection):
        Lite.DATABASE_CONNECTIONS[label] = lite_connection