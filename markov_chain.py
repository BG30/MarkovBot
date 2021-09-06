import time
from model_storage import *
import random


class MarkovModel:
    def __init__(self):
        self.__model = DataStorage()
        self.__model.setup_db()
        self.unsafe_terms = []

    def clean_db(self):
        self.__model.clean_db()

    # TODO complete functionality to not train on data which contains 'unsafe terms'
    def define_unsafe_terms(self, terms):
        for word in terms:
            self.unsafe_terms.append(self.__model.clean_data(word))

    def train_model(self, training_data):
        if training_data in self.unsafe_terms:
            return

        token_list = training_data.strip().split()
        self.__model.insert_data(self.__model.start, token_list[0])

        for i in range(len(token_list)):
            if i == len(token_list)-1:
                self.__model.insert_data(token_list[i], self.__model.end)
            elif i+1 > len(token_list):
                self.__model.insert_data(token_list[i], self.__model.end)
            else:
                self.__model.insert_data(token_list[i], token_list[i+1])

    def __generate_next_word_percentage(self, word):
        pairings = self.__model.get_neighbors(word)
        out_count = self.__model.get_number_of_out_connections(word)[0]
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

    def generate_response(self, prompt):
        random.seed(time.time())
        response_limit = self.__get_response_length(prompt)
        next_word = self.__choose_word(self.__model.start, self.__generate_next_word_percentage(self.__model.start))
        if next_word == self.__model.end:
            return ""

        # keep choosing word until terminating string returned
        i = 1
        result = [next_word]
        while True:
            next_word = self.__model.clean_data(next_word)
            if i < response_limit:
                next_word = self.__choose_word(next_word, self.__generate_next_word_percentage(next_word))
            else:
                next_word = self.search_for_word(next_word, self.__model.end)
                return " ".join(result).join(next_word)

            if next_word == self.__model.end:
                return " ".join(result)
            elif i > response_limit*2:
                # backup function termination
                return " ".join(result)
            result.append(next_word)
            i += 1

    def __choose_word(self, origin_word, percentage):
        best_word = ""
        best_difference = 2
        pairings = self.__model.get_neighbors(origin_word)
        out_count = self.__model.get_number_of_out_connections(origin_word)[0]
        for pair in pairings:
            formula = abs(percentage - pair[1]/out_count)

            if formula == 0:
                return pair[0]
            elif formula < best_difference:
                best_word = pair[0]
                best_difference = formula

        return best_word

    def search_for_word(self, origin_word, target_word):
        visited = []
        queue = [[origin_word]]

        if origin_word == target_word:
            return target_word

        while queue:
            path = queue.pop(0)
            node = path[-1]
            if node not in visited:
                # get neighbors
                neighbors = self.__model.get_neighbors(node)
                for resident in neighbors:
                    new_path = list(path)
                    new_path.append(resident[0])
                    queue.append(new_path)
                    if resident[0] == target_word:
                        return new_path
                visited.append(node)
        # default response
        return self.__model.end

    def __get_response_length(self, prompt):
        if prompt != "":
            return math.ceil(len(prompt) * random.uniform(0.5, 3))
        else:
            return 40 + random.randint(0, 20)
