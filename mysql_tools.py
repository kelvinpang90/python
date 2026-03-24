import logging
from contextlib import contextmanager
from typing import List, Dict, Any, Optional

import mysql.connector
from mysql.connector import Error

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MySQLTools:
    """MySQL utility class for database operations"""

    def __init__(self, host: str = 'localhost', port: int = 3306,
                 user: str = 'root', password: str = '123456',
                 database: str = ''):
        """
        Initialize MySQL connection

        Args:
            host: Database host address
            port: Database port
            user: Database username
            password: Database password
            database: Database name
        """
        self.config = {
            'host': host,
            'port': port,
            'user': user,
            'password': password,
            'database': database
        }
        self.connection = None
        self._connect()

    def _connect(self) -> bool:
        """Establish database connection internally"""
        try:
            self.connection = mysql.connector.connect(**self.config)
            if self.connection.is_connected():
                return True
        except Error as e:
            logger.error(f"Error connecting to MySQL: {e}")
            return False
        return False

    def _disconnect(self):
        """Close database connection internally"""
        if self.connection and self.connection.is_connected():
            self.connection.close()

    @contextmanager
    def get_cursor(self, dictionary: bool = True):
        """Context manager for cursor with automatic resource management"""
        cursor = None
        try:
            cursor = self.connection.cursor(dictionary=dictionary)
            yield cursor
        finally:
            if cursor:
                cursor.close()

    def create_table_if_not_exists(self, table_name: str, columns: Dict[str, str]) -> bool:
        """
        Create table if it doesn't exist

        Args:
            table_name: Name of the table
            columns: Dictionary of column names and their types

        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_cursor() as cursor:
                columns_sql = ', '.join([f"{col} {dtype}" for col, dtype in columns.items()])
                create_table_sql = f"""
                    CREATE TABLE IF NOT EXISTS {table_name} (
                        {columns_sql}
                    )
                """

                cursor.execute(create_table_sql)
                self.connection.commit()
                logger.info(f"Table '{table_name}' created or already exists")
                return True

        except Error as e:
            logger.error(f"Error creating table: {e}")
            return False

    def insert(self, table_name: str, data: Dict[str, Any]) -> Optional[int]:
        """
        Insert a record into the database

        Args:
            table_name: Name of the table
            data: Dictionary of column names and values

        Returns:
            Last inserted ID if successful, None otherwise
        """
        try:
            with self.get_cursor() as cursor:
                columns = ', '.join(data.keys())
                placeholders = ', '.join(['%s'] * len(data))
                insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

                cursor.execute(insert_sql, tuple(data.values()))
                self.connection.commit()

                last_id = cursor.lastrowid
                logger.info(f"Record inserted with ID: {last_id}")
                return last_id

        except Error as e:
            logger.error(f"Error inserting record: {e}")
            return None

    def select_all(self, table_name: str, conditions: Optional[Dict[str, Any]] = None,
                   order_by: Optional[str] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Select records from the database

        Args:
            table_name: Name of the table
            conditions: Optional dictionary of WHERE conditions
            order_by: Optional ORDER BY clause
            limit: Optional LIMIT clause

        Returns:
            List of records as dictionaries
        """
        try:
            with self.get_cursor() as cursor:
                select_sql = f"SELECT * FROM {table_name}"
                params = []

                if conditions:
                    where_clauses = []
                    for key, value in conditions.items():
                        where_clauses.append(f"{key} = %s")
                        params.append(value)
                    select_sql += " WHERE " + " AND ".join(where_clauses)

                if order_by:
                    select_sql += f" ORDER BY {order_by}"

                if limit:
                    select_sql += f" LIMIT {limit}"

                cursor.execute(select_sql, params)
                results = cursor.fetchall()
                logger.info(f"Retrieved {len(results)} records from '{table_name}'")
                return results

        except Error as e:
            logger.error(f"Error selecting records: {e}")
            return []

    def delete(self, table_name: str, conditions: Dict[str, Any]) -> bool:
        """
        Delete records from the database

        Args:
            table_name: Name of the table
            conditions: Dictionary of WHERE conditions

        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_cursor() as cursor:
                where_clauses = []
                params = []
                for key, value in conditions.items():
                    where_clauses.append(f"{key} = %s")
                    params.append(value)

                delete_sql = f"DELETE FROM {table_name} WHERE " + " AND ".join(where_clauses)

                cursor.execute(delete_sql, params)
                self.connection.commit()

                affected_rows = cursor.rowcount
                logger.info(f"Deleted {affected_rows} records from '{table_name}'")
                return True

        except Error as e:
            logger.error(f"Error deleting records: {e}")
            return False

    def update(self, table_name: str, data: Dict[str, Any], conditions: Dict[str, Any]) -> bool:
        """
        Update records in the database

        Args:
            table_name: Name of the table
            data: Dictionary of column names and new values
            conditions: Dictionary of WHERE conditions

        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_cursor() as cursor:
                set_clauses = []
                params = []

                for key, value in data.items():
                    set_clauses.append(f"{key} = %s")
                    params.append(value)

                where_clauses = []
                for key, value in conditions.items():
                    where_clauses.append(f"{key} = %s")
                    params.append(value)

                update_sql = f"UPDATE {table_name} SET " + ", ".join(set_clauses)
                update_sql += " WHERE " + " AND ".join(where_clauses)

                cursor.execute(update_sql, params)
                self.connection.commit()

                affected_rows = cursor.rowcount
                logger.info(f"Updated {affected_rows} records in '{table_name}'")
                return True

        except Error as e:
            logger.error(f"Error updating records: {e}")
            return False

    def execute_query(self, query: str, params: Optional[tuple] = None) -> bool:
        """
        Execute a custom SQL query

        Args:
            query: SQL query string
            params: Optional tuple of parameters

        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params or ())
                self.connection.commit()
                logger.info("Query executed successfully")
                return True

        except Error as e:
            logger.error(f"Error executing query: {e}")
            return False

    def is_connected(self) -> bool:
        """Check if database connection is active"""
        return self.connection is not None and self.connection.is_connected()

    def __del__(self):
        """Automatically disconnect when object is destroyed"""
        self._disconnect()

