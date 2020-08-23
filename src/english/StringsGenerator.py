from random import choice, choices
from string import ascii_uppercase


class StringGenerator:
    @staticmethod
    def generate_string_list(strings, generation_prob=.75):
        result = set()

        for letter in strings:
            strings.remove(letter)
            stack = [
                (strings, [letter], generation_prob)
            ]
            while stack:
                alphabet, prefix, gen_prob = stack.pop()
                stop_prob = 1 - gen_prob
                rand_num = choices(range(2), [stop_prob, gen_prob])
                if rand_num[0] == 0:
                    result.add(''.join(prefix))
                else:
                    next_letter = choice(alphabet)
                    alphabet.remove(next_letter)
                    stack.append(
                        (alphabet, prefix + [next_letter], gen_prob ** 2)
                    )
                    alphabet.append(next_letter)

            strings.append(letter)
        return result


if __name__ == '__main__':
    data = StringGenerator.generate_string_list(list(ascii_uppercase))
    multi_letter_subset_len = len(list(filter(lambda x: x > 1, map(len, data))))
    print('Set:', data)
    print('Length:', len(data))
    print('Count of multi-chars:', multi_letter_subset_len)
    print('Count of chars:', len(data) - multi_letter_subset_len)
