import sqlite3
import sys


class DBCore:
    def __init__(self, db_name):
        try:
            self.connection = sqlite3.connect(db_name)
        except:
            print("Failed to connect to database")
            sys.exit()

    def __del__(self):
        self.connection.close()

    def run_query(self, query):
        con = self.connection
        cur = con.cursor()
        return cur.execute(f'{query}')

    def update_db_query(self, query):
        con = self.connection
        cur = con.cursor()
        cur.execute(f'{query}')
        con.commit()
