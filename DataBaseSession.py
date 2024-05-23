"""
Module: DataBaseSession

This module provides a class for managing a session with a MySQL database.

Attributes:
    DATABASE_IP (str): The IP address of the MySQL database server.
    USERNAME (str): The username for connecting to the MySQL database.
    PASSWORD (str): The password for connecting to the MySQL database.

Classes:
    DataBaseSession: A class for managing a session with a MySQL database.

Usage:
    from DataBaseSession import DataBaseSession

    # Create a new database session
    db_session = DataBaseSession()

    # Execute a query to insert data into the database
    db_session.insert('INSERT INTO table_name (column1, column2) VALUES (%s, %s)', (value1, value2))

    # Execute a query to fetch data from the database
    result = db_session.fetch('SELECT * FROM table_name')

    # Close the database session
    del db_session
"""

import mysql.connector as mc
from typing import Union
DATABASE_IP = "10.100.102.204"
USERNAME = 'ariel'
PASSWORD = '112358'
class DataBaseSession:
    """
    A class for managing a session with a MySQL database.

    Attributes:
        db (MySQLConnection): The connection object for the database.
        cursor (Cursor): The cursor object for executing SQL queries.
    """

    def __init__(self) -> None:
        """
        Initialize a new database session.

        Establishes a connection to the MySQL database using the provided credentials.
        """
        self.db = mc.connect(host=DATABASE_IP, user=USERNAME, password=PASSWORD)
        self.cursor = self.db.cursor()
        self.insert('USE RAID;')

    def insert(self, query: str, values: Union[tuple, list] = None) -> None:
        """
        Execute an SQL INSERT query.

        Args:
            query (str): The SQL query to execute.
            values (Union[tuple, list], optional): The values to insert into the query. Defaults to None.

        Raises:
            mysql.connector.Error: If an error occurs while executing the query.
        """
        if isinstance(values, list):
            self.cursor.executemany(query, values)
        elif values is None:
            self.cursor.execute(query)
        else:
            self.cursor.execute(query, values)
        self.db.commit()

    def fetch(self, query: Union[tuple, str], all=False) -> iter:
        """
        Execute an SQL SELECT query and fetch the results.

        Args:
            query (Union[tuple, str]): The SQL query to execute. If a tuple, the first element
                is the query string and the second element is a tuple of query parameters.
            all (bool, optional): Whether to fetch all rows or just the first row. Defaults to False.

        Returns:
            iter: An iterator over the query results.

        Raises:
            mysql.connector.Error: If an error occurs while executing the query.
        """
        if isinstance(query, tuple):
            self.cursor.execute(query[0], query[1])
        else:
            self.cursor.execute(query)
        return self.cursor.fetchall() if all else self.cursor.fetchone()

    def __delattr__(self):
        """
        Clean up resources when the object is deleted.

        Closes the cursor and database connection.
        """
        self.cursor.close()
        self.db.close()
