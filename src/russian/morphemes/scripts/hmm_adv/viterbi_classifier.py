from src.russian.morphemes.scripts.hmm.model import HMMModelHandler


class HMMClassifier:
    def __init__(self, model):
        start_states, trans, emis = HMMModelHandler.load_model(model)
        self.start_states, self.trans, self.emis = HMMModelHandler.normalize_model(start_states, trans, emis)
        self.max_word_len = max(map(len, [t[0] for raw in self.emis for t in raw.keys()]))

    def find_the_best_partition(self, word, pos_tag=None):
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
            if pos:
                return state_prob.get((w, pos), 0)
            else:
                return sum(state_prob.get((ww, _), 0) for ww,  _ in state_prob.values() if ww == w)

        def s_prob(s):
            return self.start_states.get(s, 0)

        def st_prob(prev_state, start_state, next_state):
            if not states:
                return s_prob(start_state)
            else:
                return t_prob(states[prev_state], next_state)

        probs, lasts, states = [1.0], [0], []
        for j in range(1, len(word) + 1):
            prob, k, st = max((probs[t] * e_prob(word[t:j], pos_tag, st) * st_prob(t, start, st), t, st)
                              for t in range(max(0, len(word) - self.max_word_len))
                              for st in HMMModelHandler.get_states()
                              for start in [0, 1])
            probs.append(prob)
            states.append(st)
            lasts.append(k)

        morphs = []
        i = len(word)
        while i > 0:
            morphs.append(
                (word[lasts[i]:i], HMMModelHandler.decode_label(states[i]))
            )
            i = lasts[i]

        return reversed(morphs)
