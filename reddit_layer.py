from markov_chain import *
from keys import *


class RedditLayer:
    def __init__(self):
        self.__db = DBCore('postCode.db')
        self.__setup_comment_id_history()
        self.__model = MarkovModel()
        self.user = self.__setup_reddit_api()

    def __del__(self):
        pass

    def __setup_reddit_api(self):
        return get_reddit_credentials()

    def reply_to_comment(self, response, comment_instance):
        if self.find_id(comment_instance):
            # id found thus not responding
            return 1
        else:
            # id not found thus responding to it
            self.store_comment_id(comment_instance.id)
            comment_instance.reply(response)

    def find_id(self, comment_instance):
        query = f"SELECT count(*) FROM post WHERE post.'id'='{comment_instance.id}';"
        val = self.__db.run_query(query).fetchone()
        if val[0] == 0:
            return False
        else:
            return True

    def train_on_data(self, comment_instance):
        if not hasattr(comment_instance, "body"):
            return

        if self.find_id(comment_instance):
            # comment_instance already interacted with
            return
        else:
            self.__model.train_model(comment_instance.body.lower())
            self.store_comment_id(comment_instance)

    def __setup_comment_id_history(self):
        query = """
                            CREATE TABLE IF NOT EXISTS post (
                                id varchar(7) PRIMARY KEY
                            );
                        """
        self.__db.update_db_query(query)

    def store_comment_id(self, comment_instance):
        query = f"INSERT INTO post(id) VALUES('{comment_instance.id}');"
        self.__db.update_db_query(query)
