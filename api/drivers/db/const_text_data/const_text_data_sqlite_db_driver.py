from .const_text_data_db_driver_interface import *

import sqlite3


class ConstTextDataSQLiteDBDriver(ConstTextDataDBDriverInterface):
    __CREATE_TABLE_QUERY = """
    CREATE TABLE %s (
        id INTEGER PRIMARY KEY NOT NULL,
        text_data TEXT
    );
    """

    __GET_QUERY = """
    SELECT * FROM %s WHERE id=%i;
    """

    __PUT_QUERY = """
    INSERT INTO %s 
    (text_data) VALUES (%s);
    """

    __LAST_ENTRY_QUERY = """
    SELECT * FROM %s ORDER BY id DESC LIMIT 1;
    """

    def __init__(self, file_path: str, table: str):
        self.__connection = sqlite3.connect(file_path)
        self.__table = table

    def __del__(self):
        self.__connection.close()

    def create_table(self):
        cursor = self.__get_cursor()
        cursor.execute(self.__CREATE_TABLE_QUERY % self.__table)

    def get_data(self, id: int) -> ConstTextData:
        cursor = self.__get_cursor()
        cursor.execute(
            self.__GET_QUERY % (self.__table, id)
        )
        fetch = cursor.fetchone()
        if fetch is None:
            return ConstTextData.null()
        data = ConstTextData(*cursor.fetchone())
        return data

    def put_data(self, text: str) -> ConstTextData:
        cursor = self.__get_cursor()
        cursor.execute(
            self.__PUT_QUERY % (self.__table, text)
        )
        self.__connection.commit()
        return self.__get_last_entry()

    def __get_last_entry(self) -> ConstTextData:
        cursor = self.__get_cursor()
        cursor.execute(self.__LAST_ENTRY_QUERY % self.__table)
        data = ConstTextData(*cursor.fetchone())
        return data

    def __get_cursor(self):
        return self.__connection.cursor()
