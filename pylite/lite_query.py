"""Contains the LiteQuery class """
from pylite import LiteTable, LiteCollection, Lite


class LiteQuery:
    """This class is used to create and execute queries on a LiteModel."""

    def __init__(self, lite_model, column_name: str):
        """Initializes a new LiteQuery.

        Args:
            lite_model (LiteModel): The LiteModel to query.
            column_name (str): The column within the LiteModel to query.
        """

        self._check_single_word(column_name)

        self.model = lite_model
        self.where_clause = ""
        self.params = []

        table_name = Lite.HelperFunctions.pluralize_noun(self.model.__name__.lower())

        if self.model.DEFAULT_CONNECTION is not None:
            lite_connection = self.model.DEFAULT_CONNECTION
        else:
            lite_connection = Lite.DEFAULT_CONNECTION

        if hasattr(self.model, "table_name"):
            table_name = self.model.table_name

        self.table = LiteTable(table_name, lite_connection)

        self.where_clause = f" WHERE {column_name}"

    def _check_single_word(self, value):
        """Checks if the value is a single word.
        Used to limit complex queries passed as strings."""

        if not isinstance(value, str):
            return
        words = value.split()
        if len(words) > 1:
            raise ValueError(f"LiteQuery method inputs must be a single word: {value}")

    def is_equal_to(self, value):
        """Checks if the column is equal to the value"""

        return self._add_to_query(value, " = ?")

    def is_not_equal_to(self, value):
        """Checks if the column is not equal to the value"""

        return self._add_to_query(value, " != ?")

    def is_greater_than(self, value):
        """Checks if the column is greater than the value"""

        return self._add_to_query(value, " > ?")

    def is_greater_than_or_equal_to(self, value):
        """Checks if the column is greater than or equal to the value"""

        return self._add_to_query(value, " >= ?")

    def is_less_than(self, value):
        """Checks if the column is less than the value"""

        return self._add_to_query(value, " < ?")

    def is_less_than_or_equal_to(self, value):
        """Checks if the column is less than or equal to the value"""

        return self._add_to_query(value, " <= ?")

    def is_like(self, value):
        """Checks if the column is like the value"""

        return self._add_to_query(value, " LIKE ?")

    def is_not_like(self, value):
        """Checks if the column is not like the value"""

        return self._add_to_query(value, " NOT LIKE ?")

    def _add_to_query(self, value, arg1):
        """Adds the value and argument to the query"""

        self._check_single_word(value)
        self.where_clause += arg1
        self.params.append(value)
        return self

    def starts_with(self, value):
        """Checks if the column starts with the value"""

        self._check_single_word(value)
        self.where_clause += " LIKE ?"
        self.params.append(f"{value}%")
        return self

    def ends_with(self, value):
        """Checks if the column ends with the value"""

        self._check_single_word(value)
        self.where_clause += " LIKE ?"
        self.params.append(f"%{value}")
        return self

    def is_in(self, values):
        """Checks if the column is in the given values list"""

        self.where_clause += f" IN ({ ','.join('?' * len(values)) })"
        for value in values:
            self.params.append(value)
        return self

    def contains(self, value):
        """Checks if the column contains the value"""

        return self._contains_handler(value, " LIKE ?")

    def does_not_contain(self, value):
        """Checks if the column does not contain the value"""

        return self._contains_handler(value, " NOT LIKE ?")

    def _contains_handler(self, value, arg1):
        self._check_single_word(value)
        self.where_clause += arg1
        self.params.append(f"%{value}%")
        return self

    def or_where(self, column_name):
        """Adds an OR clause to the query"""

        return self._where_handler(column_name, " OR ")

    def and_where(self, column_name):
        """Adds an AND clause to the query"""

        return self._where_handler(column_name, " AND ")

    def _where_handler(self, column_name, arg1):
        self._check_single_word(column_name)
        self.where_clause += f"{arg1}{column_name}"
        return self

    def all(self):
        """Executes the query and returns a LiteCollection"""

        query = f"SELECT id FROM {self.table.table_name}{self.where_clause}"
        rows = self.table.connection.execute(query, self.params).fetchall()
        collection = [self.model.find(row[0]) for row in rows]
        return LiteCollection(collection)

    def first(self):
        """Executes the query and returns the first result"""
        return self._extents_handler(" LIMIT 1")

    def last(self):
        """Executes the query and returns the last result"""
        return self._extents_handler(" ORDER BY id DESC LIMIT 1")

    def _extents_handler(self, arg0):
        where_clause = self.where_clause
        query = f"SELECT id FROM {self.table.table_name}{where_clause}{arg0}"
        row = self.table.connection.execute(query, self.params).fetchone()
        return self.model.find(row[0]) if row else None
