from core_db_functions import *
from markov_chain import *


class RedditLayer:
    def __init__(self):
        self.__db = DBCore('postCode.db')
        self.__setup_comment_id_history()
        self.__model = MarkovModel()

    def reply_to_comment(self, response, comment_instance):
        if self.find_id():
            # id found thus not responding
            pass
        else:
            # id not found thus responding to it
            self.store_comment_id(comment_instance.id)
            comment_instance.reply(response)

    def find_id(self, comment_id):
        query = f"SELECT count(*) FROM post WHERE post.'id'='{comment_id}';"
        val = self.db.run_query(query).fetchone()
        if val[0] == 0:
            return False
        else:
            return True

    def train_on_data(self, comment_instance):
        pass

    def __setup_comment_id_history(self):
        query = """
                            CREATE TABLE IF NOT EXISTS post (
                                id varchar(7) PRIMARY KEY
                            );
                        """
        self.__db.update_db_query(query)

    def store_comment_id(self, comment_instance):
        query = f"INSERT INTO post(id) VALUES('{comment_instance.id}');"
        self.db.update_db_query(query)
