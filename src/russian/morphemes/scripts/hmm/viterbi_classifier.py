from src.russian.morphemes.scripts.hmm.model import HMMModelHandler


class HMMClassifier:
    def __init__(self, model):
        start_states, trans, emis = HMMModelHandler.load_model(model)
        self.start_states, self.trans, self.emis = HMMModelHandler.normalize_model(start_states, trans, emis)

    def find_morphemes(self, word):
        # must return the best combination of morphemes (used Viterbi algorithm)
        def t_prob(s1, s2):
            return self.trans[s1][s2] or 0

        def e_prob(i, pos, s):
            return self.emis[s][(word[:i], pos)]

        def s_prob(s):
            return self.start_states[s]


        pass


