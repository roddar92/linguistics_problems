import os
import re


NOUN_REPLACEMENT_RULES = {
    re.compile(r'(ого|его)$'): r'[\1/END]',
    re.compile(r'(?<![аеиоуыэюя])([аеиоуыэюя])$'): r'[\1/END]',
    re.compile(r'(?<![аеиоуыэюя])([аеиоуыэюя])\['): r'[\1/END][',
    re.compile(r'(ая|ай|ий|ой|ый|ые|ою|ия|ие|ии|ию|ей|ую|ее|ое)$'): r'[\1/END]',
    re.compile(r'(ом|ов|ам|ем|им|ым|ит|ах|их|ых)$'): r'[\1/END]',
    re.compile(r'(знь)$'): r'[\1/SFX]',
    re.compile(r'([аеёи]нн?|нн?)\['): r'[\1/SFX][',
    re.compile(r'(ович|ость|ост|ичн|тель?|ниц|ник|щик|ств|ск|ек|ик|ок|чк|чн|ич|зн|ст|сн)\['): r'[\1/SFX][',
    re.compile(r'(ен|ов)\['): r'[\1/IFX][',
    re.compile(r'^(не|во[зс]|пере|бе[зс]|пр[иео]|об|анти|пред|под|вы|по|ра[зс])'): r'[\1/AFX]'
}


VERB_REPLACEMENT_RULES = {
    re.compile(r'(с[ья])$'): r'[\1/PSFX]',
    re.compile(r'([уюаяеи]те?)$'): r'[\1/END]',
    re.compile(r'([уюаяеи]те?)\['): r'[\1/END][',
    re.compile(r'([уюаяеи]шь)$'): r'[\1/END]',
    re.compile(r'([уюаяеи]шь)\['): r'[\1/END][',
    re.compile(r'(ть)\['): r'[\1/END][',
    re.compile(r'(ть)$'): r'[\1/END]',
    re.compile(r'([аеиоуыэюя])\[ть'): r'[\1/SFX][ть',
    re.compile(r'(?<![аеиоуыэюя])([аеиоуыэюя])$'): r'[\1/END]',
    re.compile(r'(?<![аеиоуыэюя])([аеиоуыэюя])\['): r'[\1/END][',
    re.compile(r'(я)$'): r'[\1/SFX]',
    re.compile(r'([уюаяи]щ|вш|енн|инн|нн)\['): r'[\1/SFX][',
    re.compile(r'([аяие]л)\['): r'[\1/SFX][',
    re.compile(r'([нкш])\['): r'[\1/SFX][',
    re.compile(r'(ом|ов|ам|ем|им|ым)$'): r'[\1/SFX]',
    re.compile(r'(ич)\['): r'[\1/SFX][',
    re.compile(r'^(не|во[зс]|пере|бе[зс]|пр[иео]|об|анти|пред|под|вы|по|ра[зс])'): r'[\1/AFX]'
}


EXCEPTED_POS = ['CONJ', 'PR', 'NONLEX', 'S-PRO', 'PART']


def apply_rules(word_tuple):
    word, pos = word_tuple
    rules = NOUN_REPLACEMENT_RULES if pos in 'S A A-PRO'.split() else VERB_REPLACEMENT_RULES
    for replacement_cond, replacement_rule in rules.items():
        word = replacement_cond.sub(replacement_rule, word)
    return word


def annotate_morphemes(input_dir, output_dir, path_to_filename):
    with open(os.path.join(input_dir, path_to_filename), 'r', encoding='utf-8') as f1, \
            open(os.path.join(output_dir, path_to_filename), 'w', encoding='utf-8') as f2:
        for line in f1.readlines():
            t = tuple(eval(line.strip()))
            t_new = (apply_rules(t), t[-1]) if t[-1] not in EXCEPTED_POS else t
            f2.write(str(t_new))
            f2.write('\n')
            f2.flush()


def main(input_dir, output_dir):
    for f in os.listdir(input_dir):
        annotate_morphemes(input_dir, output_dir, f)


if __name__ == '__main__':
    INPUT_DIR = '../../resources/corpora/output'
    OUTPUT_DIR = '../../resources/corpora/annotated'
    main(INPUT_DIR, OUTPUT_DIR)
