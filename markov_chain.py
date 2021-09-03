import time
from model_storage import *
import random


class MarkovModel:
    def __init__(self):
        self.model = DataStorage()
        self.model.setup_db()
        self.unsafe_terms = []

    def clean_db(self):
        self.model.clean_db()

    def define_unsafe_terms(self, terms):
        for word in terms:
            self.unsafe_terms.append(self.model.clean_data(word))

    def train_model(self, training_data):
        if self.unsafe_terms in training_data:
            return

        token_list = training_data.strip().split()
        self.model.insert_data(self.model.start, token_list[0])

        for i in range(len(token_list)):
            if i == len(token_list)-1:
                self.model.insert_data(token_list[i], self.model.end)
            elif i+1 > len(token_list):
                self.model.insert_data(token_list[i], self.model.end)
            else:
                self.model.insert_data(token_list[i], token_list[i+1])

    def __generate_next_word_percentage(self, word):
        pairings = self.model.get_neighbors(word)
        out_count = self.model.get_number_of_out_connections(word)[0]
        percent_lower = 2
        percent_higher = 0
        for pair in pairings:
            formula = pair[1] / out_count
            if formula > percent_higher:
                percent_higher = formula
            if formula < percent_lower:
                percent_lower = formula

        result = random.uniform(percent_lower, percent_higher)
        return result

    def generate_response(self):
        random.seed(time.time())
        response_limit = self.model.get_response_length()
        next_word = self.__choose_word(self.model.start, self.__generate_next_word_percentage(self.model.start))
        if next_word == self.model.end:
            return ""

        # keep choosing word until terminating string returned
        i = 1
        result = [next_word]
        while True:
            next_word = self.model.clean_data(next_word)
            if i <= response_limit:
                next_word = self.__choose_word(next_word, self.__generate_next_word_percentage(next_word))
            else:
                next_word = self.__choose_terminating_word(next_word, self.__generate_next_word_percentage(next_word))

            if next_word == self.model.end:
                return result
            elif i > response_limit*2:
                return result
            result.append(next_word)
            i += 1

    def __choose_terminating_word(self, origin_word, percentage):
        pairings = self.model.get_neighbors(origin_word)
        for pair in pairings:
            if pair[0] == self.model.end:
                return self.model.end
        return self.__choose_word(origin_word, percentage)

    def __choose_word(self, origin_word, percentage):
        best_word = ""
        best_difference = 2
        pairings = self.model.get_neighbors(origin_word)
        out_count = self.model.get_number_of_out_connections(origin_word)[0]
        for pair in pairings:
            formula = abs(percentage - pair[1]/out_count)

            if formula == 0:
                return pair[0]
            elif formula < best_difference:
                best_word = pair[0]
                best_difference = formula

        return best_word
