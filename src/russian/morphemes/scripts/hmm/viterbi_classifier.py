from src.russian.morphemes.scripts.hmm.model import HMMModelHandler


class HMMClassifier:
    def __init__(self, model):
        start_states, trans, emis = HMMModelHandler.load_model(model)
        self.start_states, self.trans, self.emis = HMMModelHandler.normalize_model(start_states, trans, emis)
        self.max_word_len = max(map(len, [t[0] for raw in self.emis for t in raw.keys()]))

    def find_the_best_partition(self, word, pos_tag):
        # return the best combination of morphemes (used Viterbi algorithm)
        def t_prob(s1, s2):
            state_prob = self.trans.get(s1, {})
            if not state_prob:
                return 0
            return state_prob.get(s2, 0)

        def e_prob(w, pos, s):
            state_prob = self.emis.get(s, {})
            if not state_prob:
                return 0
            return state_prob.get((w, pos), 0)

        def s_prob(s):
            return self.start_states.get(s, 0)

        probs, morphs, lasts, states = [], [], [], []
        prob, k, st = max((s_prob(st) * e_prob(word[0:k], pos_tag, st), k, st)
                          for k in range(max(0, len(word) - self.max_word_len))
                          for st in HMMModelHandler.get_states())
        probs.append(prob)
        states.append(st)
        lasts.append(k)
        for j in range(k, len(word) + 1):
            prob, k, st = max(probs[t] * (e_prob(word[t:j], pos_tag, st) * t_prob(states[t], st), k, st)
                              for t in range(max(0, len(word) - self.max_word_len))
                              for st in HMMModelHandler.get_states())
            probs.append(prob)
            states.append(st)
            lasts.append(k)

        i = len(word)
        while i > 0:
            morphs.append(word[lasts[i]:i])
            i = lasts[i]

        return [(morph, HMMModelHandler.decode_label(s)) for morph, s in zip(reversed(morphs), states)]
