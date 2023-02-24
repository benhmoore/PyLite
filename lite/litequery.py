""" Contains the LiteQuery class """
from lite import LiteTable, LiteModel, LiteCollection, Lite
# from lite.liteexceptions import ModelInstanceNotFoundError, RelationshipError

class LiteQuery:
    def __init__(self, lite_model: LiteModel, column_name: str):
        self._check_single_word(column_name)

        self.model = lite_model
        self.where_clause = ""
        self.params = []

        table_name = Lite.pluralize_noun(self.model.__name__.lower())

        if self.model.DEFAULT_CONNECTION is not None:
            lite_connection = self.model.DEFAULT_CONNECTION
        else:
            lite_connection = Lite.DEFAULT_CONNECTION

        if hasattr(self.model, 'table_name'):
            table_name = self.model.table_name

        self.table = LiteTable(table_name, lite_connection)

        self.where_clause = f" WHERE {column_name}"

    def _check_single_word(self, value):
        if not isinstance(value, str):
            return
        words = value.split()
        if len(words) > 1:
            raise ValueError(f"LiteQuery method inputs must be a single word: {value}")

    def is_equal_to(self, value):
        self._check_single_word(value)
        self.where_clause += " = ?"
        self.params.append(value)
        return self

    def is_not_equal_to(self, value):
        self._check_single_word(value)
        self.where_clause += " != ?"
        self.params.append(value)
        return self

    def is_greater_than(self, value):
        self._check_single_word(value)
        self.where_clause += " > ?"
        self.params.append(value)
        return self

    def is_greater_than_or_equal_to(self, value):
        self._check_single_word(value)
        self.where_clause += " >= ?"
        self.params.append(value)
        return self

    def is_less_than(self, value):
        self._check_single_word(value)
        self.where_clause += " < ?"
        self.params.append(value)
        return self

    def is_less_than_or_equal_to(self, value):
        self._check_single_word(value)
        self.where_clause += " <= ?"
        self.params.append(value)
        return self

    def is_like(self, value):
        self._check_single_word(value)
        self.where_clause += " LIKE ?"
        self.params.append(value)
        return self

    def is_not_like(self, value):
        self._check_single_word(value)
        self.where_clause += " NOT LIKE ?"
        self.params.append(value)
        return self

    def starts_with(self, value):
        self._check_single_word(value)
        self.where_clause += " LIKE ?"
        self.params.append(value + "%")
        return self

    def ends_with(self, value):
        self._check_single_word(value)
        self.where_clause += " LIKE ?"
        self.params.append("%" + value)
        return self

    def contains(self, value):
        self._check_single_word(value)
        self.where_clause += " LIKE ?"
        self.params.append("%" + value + "%")
        return self

    def or_where(self, column_name):
        self._check_single_word(column_name)
        self.where_clause += f" OR {column_name}"
        return self

    def and_where(self, column_name):
        self._check_single_word(column_name)
        self.where_clause += f" AND {column_name}"
        return self

    def _execute_query(self):
        query = f"SELECT id FROM {self.table.table_name}{self.where_clause}"
        rows = self.table.connection.execute(query, self.params).fetchall()
        collection = [self.model.find_or_fail(row[0]) for row in rows]
        return LiteCollection(collection)
    
    def all(self):
        return self._execute_query()
    
    def first(self):
        return self.all().first()
    
    def last(self):
        return self.all().last()
    
    # def first(self):
    #     query = f"SELECT id FROM {self.table.table_name}{self.where_clause} ORDER BY id ASC LIMIT 1"
    #     rows = self.table.connection.execute(query, tuple()).fetchall()
    #     if len(rows) == 0:
    #         return None
    #     return self.model.find_or_fail(rows[0][0])

    # def last(self):
    #     query = f"SELECT id FROM {self.table.table_name}{self.where_clause} ORDER BY id DESC LIMIT 1"
    #     rows = self.table.connection.execute(query, tuple()).fetchall()
    #     if len(rows) == 0:
    #         return None
    #     return self.model.find_or_fail(rows[0][0])
        