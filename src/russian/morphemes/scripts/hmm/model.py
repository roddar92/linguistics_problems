import pickle
import os
from collections import Counter, defaultdict
from sklearn.preprocessing import LabelEncoder


class HMMModelHandler:
    encoder = LabelEncoder()

    def __init__(self, states):
        self.states = states
        self.encoder.fit(self.states)

        self.starts = Counter()
        self.transitions = defaultdict(Counter)
        self.emissions = defaultdict(Counter)

    @classmethod
    def encode_label(cls, label):
        return cls.encoder.transform(label)

    @classmethod
    def decode_label(cls, label):
        return cls.encoder.inverse_transform(label)

    @classmethod
    def get_states(cls):
        return cls.encoder.classes_

    def save_model(self, path_to_model):
        probs = (self.starts, self.transitions, self.emissions)
        pickle.dump(probs, open(path_to_model + '-hmm.pkl', 'wb'))

    @staticmethod
    def load_model(path_to_model):
        full_model_name = path_to_model + '-hmm.pkl'
        (starts, transitions, emissions) = pickle.load(open(full_model_name, 'wb'))
        return starts, transitions, emissions

    def store_probabilities(self, line, delimiter='][', annot_delimiter='/'):
        prev_state = None
        annotation, pos = tuple(eval(line))
        for element in annotation.split(delimiter):
            if element.startswith(delimiter[-1]):
                element = element[1:]
            elif element.endswith(delimiter[0]):
                element = element[:-1]
            observation, state = element.split(annot_delimiter)

            s = self.encoder.transform(state)
            self.emissions[s][(observation, pos)] += 1
            if not prev_state:
                self.starts[s] += 1
            else:
                s1 = self.encoder.transform(prev_state)
                self.transitions[s1][s] += 1
            prev_state = state

    def collect_model(self, input_dir):
        for f in os.listdir(input_dir):
            with open(os.path.join(input_dir, f), 'r', encoding='utf-8') as fin:
                for line in fin.readlines():
                    self.store_probabilities(line=line.strip())

    def update_model(self, input_dir, path_to_model):
        if not (self.starts or self.transitions or self.emissions):
            self.starts, self.transitions, self.emissions = self.load_model(path_to_model=path_to_model)
        self.collect_model(input_dir=input_dir)
        self.save_model(path_to_model=path_to_model)

    @staticmethod
    def normalize_model(starts, transitions, emissions):
        total_starts = sum(starts.values())
        starts = {
            k: float(v / total_starts) for k, v in starts.items()
        }

        for k in transitions:
            trans_k_total = sum(transitions[k].values())
            transitions[k] = {
                kk: float(v / trans_k_total) for kk, v in transitions[k].items()
            }

        for k in emissions:
            emis_k_total = sum(emissions[k].values())
            emissions[k] = {
                kk: float(v / emis_k_total) for kk, v in emissions[k].items()
            }

        return starts, transitions, emissions
