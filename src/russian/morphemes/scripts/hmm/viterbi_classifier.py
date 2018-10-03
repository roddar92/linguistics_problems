from src.russian.morphemes.scripts.hmm.model import HMMModelHandler


class HMMClassifier:
    def __init__(self, model):
        start_states, trans, emis = HMMModelHandler.load_model(model)
        self.start_states, self.trans, self.emis = HMMModelHandler.normalize_model(start_states, trans, emis)
        self.max_word_len = max(map(len, [t[0] for raw in self.emis for t in raw.keys()]))

    def find_morphemes(self, word, pos_tag):
        # must return the best combination of morphemes (used Viterbi algorithm)
        def t_prob(s1, s2):
            return self.trans[s1][s2] or 0

        def e_prob(w, pos, s):
            return self.emis[s][(w, pos)]

        def s_prob(s):
            return self.start_states[s]

        probs, morphs, lasts, states = [], [], [], []
        prob, k, st = max((s_prob(st) * e_prob(word[0:k], pos_tag, st), k, st)
                          for k in range(max(0, len(word) - self.max_word_len))
                          for st in HMMModelHandler.get_states())
        for j in (k, len(word) + 1):
            prob, k, st = max(probs[t] * (e_prob(word[t:j], pos_tag, st) * t_prob(states[t], st), k, st)
                              for t in range(max(0, len(word) - self.max_word_len))
                              for st in HMMModelHandler.get_states())

        return [(morph, HMMModelHandler.decode_label(s)) for morph, s in zip(reversed(morphs), states)]
