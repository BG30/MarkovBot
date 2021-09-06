import math

from core_db_functions import *
import random


class DataStorage:
    def __init__(self):
        self.start = '__START__'
        self.end = '__TERMINATE__'
        self.__db = DBCore('modelData.db')

    def setup_db(self):
        query = """
                    CREATE TABLE IF NOT EXISTS state (
                        word varchar(50) PRIMARY KEY,
                        outCount int
                    );
                """
        self.__db.update_db_query(query)

        query = """
                    CREATE TABLE IF NOT EXISTS occurrences (
                        word VARCHAR(50),
                        partnerWord VARCHAR(50) REFERENCES state(word),
                        tally int,
                        PRIMARY KEY(word, partnerWord)
                    );
                """
        self.__db.update_db_query(query)

        self.__db.update_db_query(f'INSERT OR IGNORE INTO state VALUES("{self.start}", 0);')
        self.__db.update_db_query(f'INSERT OR IGNORE INTO state VALUES("{self.end}", 0);')

    def clean_db(self):
        self.__db.update_db_query(f"DELETE FROM occurrences;")
        self.__db.update_db_query(
            f'DELETE FROM state WHERE word <> "{self.start}" OR word <> "{self.end}";')

    def insert_data(self, origin_word, target_word):
        origin_word = self.clean_data(origin_word)
        target_word = self.clean_data(target_word)

        # check if origin and target word already in db and insert as needed
        self.__db.update_db_query(f' INSERT OR IGNORE INTO state VALUES ("{origin_word}", 0); ')
        self.__db.update_db_query(f' INSERT OR IGNORE INTO state VALUES ("{target_word}", 0); ')

        # if occurrence present then increase tally else insert new occurrence
        self.__db.update_db_query(f'INSERT OR IGNORE INTO occurrences VALUES ("{origin_word}", "{target_word}", 0);')
        self.__db.update_db_query(
            f'UPDATE occurrences SET tally = tally + 1 WHERE word = "{origin_word}" AND partnerWord="{target_word}";'
        )
        self.__db.update_db_query(f'UPDATE state SET outCount = outCount + 1 WHERE word = "{origin_word}"')

    def get_neighbors(self, origin_word):
        result = self.__db.run_query(f'SELECT partnerWord, tally FROM occurrences WHERE word = "{origin_word}";')
        return result.fetchall()

    def get_number_of_out_connections(self, word):
        result = self.__db.run_query(f'SELECT outCount FROM state WHERE word = "{word}";')
        return result.fetchone()

    def clean_data(self, word):
        word = word.replace('"', '\"\"')
        word = word.replace("'", "\'")
        return word
