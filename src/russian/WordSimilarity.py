CONSONANT_GROUPS = [
    {'в', 'м', 'б', 'п', 'ф'},
    {'л', 'р', 'с', 'т', 'д', 'н'},
    {'х', 'ц', 'к', 'г', 'з', 'ж'},
    {'в', 'р', 'х'},
    {'с', 'ц', 'ч'}
]


def is_consonant(letter):
    return letter in 'бвгджзклмнпрстфхцчшщ'


def is_vowel(letter):
    return letter in 'аеёиоуыэю'


def is_in_simillar_group(letter1, letter2):
    return any(letter1 in group and letter2 in group for group in CONSONANT_GROUPS)


def check_similarity(word1, word2):
    i, j = 0, 0
    s, t, m, n = 0, 0, 0, 0
    while i < len(word1) and j < len(word2):
        l1, l2 = word1[i], word2[j]
        if (l1 == 'ь' or is_vowel(l1)) and (l2 == 'ь' or is_vowel(l2)):
            i += 1
            j += 1
        elif l1 == 'ь' or is_vowel(l1):
            i += 1
        elif l2 == 'ь' or is_vowel(l2):
            j += 1
        else:
            if is_consonant(l1) and is_consonant(l2) and (l1 == l2 or is_in_simillar_group(l1, l2)):
                i += 1
                j += 1
                m += 1
                n += 1
                s += 1
                t += 1
            elif is_consonant(l1):
                m += 1
                i += 1
            else:
                n += 1
                j += 1

    while i < len(word1):
        if is_consonant(word1[i]):
            m += 1
        i += 1

    while j < len(word2):
        if is_consonant(word2[j]):
            n += 1
        j += 1

    return float(s + t) / (m + n)


if __name__ == '__main__':
    print(check_similarity('глобус', 'колобок'))
    print(check_similarity('смог', 'мгла'))
    print(check_similarity('лаборатория', 'работа'))
    print(check_similarity('калькулятор', 'сколько'))
    print(check_similarity('доллар', 'доля'))
    print(check_similarity('галактика', 'галага'))
    print(check_similarity('леди', 'лада'))
