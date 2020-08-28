from collections import Counter
from random import choice, choices
from string import ascii_uppercase, ascii_lowercase


class StringGenerator:
    @staticmethod
    def generate_string_list(strings, generation_prob=.75):
        result = set()

        for curr_str in strings:
            strings.remove(curr_str)
            stack = [
                (strings, [curr_str], generation_prob)
            ]
            while stack:
                rest_strings, prefix, gen_prob = stack.pop()
                stop_prob = 1 - gen_prob
                rand_num = choices([0, 1], [stop_prob, gen_prob])[-1]
                if rand_num == 0:
                    full_string = ''.join(prefix)
                    result.add(full_string)
                else:
                    next_str = choice(rest_strings)
                    rest_strings.remove(next_str)
                    stack.append(
                        (rest_strings, prefix + [next_str], gen_prob ** 2)
                    )
                    rest_strings.append(next_str)

            strings.append(curr_str)
        return result


if __name__ == '__main__':
    data = StringGenerator.generate_string_list(list(ascii_uppercase + ascii_lowercase))
    multi_letter_subset = list(filter(lambda x: x > 1, map(len, data)))
    print('Set:', data)
    print('Length:', len(data))
    print('Count of multi-chars:', len(multi_letter_subset))
    print('Count of chars:', len(data) - len(multi_letter_subset))
    print('Fetched lengths:')
    for l, count in Counter(map(len, data)).most_common():
        print(f'Length: {l} - Count: {count}')
