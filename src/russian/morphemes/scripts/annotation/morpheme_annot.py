import os
import re


RT = r'([^\[\]]+)'
ROOT = re.compile(r'(.+)')
NOUN_SUFFIXES = r'(ович|ость|ост|ичн|тель?|ниц|ник|щик|енк|ньк|ушк|ичн|ист|изм|ств|ск|ек|ик|ок|чк|оч|чн|ич|яч|зн|ст|сн|к)'
PAST_VB_SFX = r'([аяиеыё]л)'
ENDING = r'(?<![аеиоуыэюя])([аеиоуыэюя])'
ADJ_ENDINGS = r'(ая|ай|ий|ой|ый|ые|ою|ия|ие|ии|ию|ей|ую|ее|ое)'
VERB_ENDINGS = r'([уюаяеи]те?)'
AFFIX = r'(не|во[зс]|пере|бе[зс]|пр[иео]|обо?|анти|пред|под|вы|по|ра[зс]|у|о|за|из|до|от)'

NOUN_REPLACEMENT_RULES = {
    re.compile(r'(?<!^)' + r'(ого|его)$'): r'[\1/END]',
    re.compile(r'(?<!^)' + ENDING + r'$'): r'[\1/END]',
    re.compile(r'(?<!^)' + ENDING + r'\['): r'[\1/END][',
    re.compile(r'(?<!^)' + ADJ_ENDINGS + r'$'): r'[\1/END]',
    re.compile(r'(?<!^)(ом|ов|ам|ем|им|ым)\['): r'[\1/END][',
    re.compile(r'(?<!^)(ом|ов|ам|ем|им|ым|ах|их|ых)$'): r'[\1/END]',
    re.compile(r'(?<!^)(знь)$'): r'[\1/SFX]',
    re.compile(r'(?<!^)([аеёи]нн?|нн?)\['): r'[\1/SFX][',
    re.compile(r'(?<!^)' + NOUN_SUFFIXES + '\['):
        r'[\1/SFX][',
    re.compile(r'(?<!^)' + NOUN_SUFFIXES + '$'):
        r'[\1/SFX]',
    re.compile(r'(ен|ов)\['): r'[\1/IFX][',
    re.compile(r'^' + AFFIX + r'(?!$)'): r'[\1/AFX]',
    re.compile(r'\]' + RT + r'\['): r'][\1/RT][',
    re.compile(r'^' + RT + r'\['): r'[\1/RT]['
}


VERB_REPLACEMENT_RULES = {
    re.compile(r'(?<!^)' + r'(с[ья])$'): r'[\1/PSFX]',
    re.compile(r'(?<!^)' + VERB_ENDINGS + r'$'): r'[\1/END]',
    re.compile(r'(?<!^)' + VERB_ENDINGS + r'\['): r'[\1/END][',
    re.compile(r'(?<!^)' + ADJ_ENDINGS + r'$'): r'[\1/END]',
    re.compile(r'(?<!^)' + r'([уюаяеи]шь)$'): r'[\1/END]',
    re.compile(r'(?<!^)' + r'([уюаяеи]шь)\['): r'[\1/END][',
    re.compile(r'(?<!^)' + r'(ть)\['): r'[\1/END][',
    re.compile(r'(?<!^)' + r'(ть)$'): r'[\1/END]',
    re.compile(r'(?<!^)([аеиоуыэюя])\[ть'): r'[\1/SFX][ть',
    re.compile(r'(?<!^)' + ENDING + r'$'): r'[\1/END]',
    re.compile(r'(?<!^)' + ENDING + r'\['): r'[\1/END][',
    re.compile(r'(?<!^)' + r'(я)$'): r'[\1/SFX]',
    re.compile(r'(?<!^)([уюаяи]щ|вш|енн|инн|нн)\['): r'[\1/SFX][',
    re.compile(r'(?<!^)' + PAST_VB_SFX + '\['): r'[\1/SFX][',
    re.compile(r'(?<!^)' + PAST_VB_SFX + r'$'): r'[\1/SFX]',
    re.compile(r'(?<!^)([нкш])\['): r'[\1/SFX][',
    re.compile(r'(?<!^)(ом|ов|ам|ем|им|ым)$'): r'[\1/SFX]',
    re.compile(r'(?<!^)(ич)\['): r'[\1/SFX][',
    re.compile(r'^' + AFFIX + r'(?!$)'): r'[\1/AFX]',
    re.compile(r'\]' + RT + r'\['): r'][\1/RT][',
    re.compile(r'^' + RT + r'\['): r'[\1/RT]['
}


EXCEPTED_POS = ['CONJ', 'PR', 'NONLEX', 'S-PRO', 'ADV-PRO', 'PART', 'PRAEDIC']


def apply_rules(word_tuple):
    def is_long_seq(word):
        return len(word) > 3

    word, pos = word_tuple
    word = re.sub(r'ё', 'е', word)
    rules = NOUN_REPLACEMENT_RULES if pos in 'S A A-PRO NUM'.split() else VERB_REPLACEMENT_RULES
    if is_long_seq(word):
        for replacement_cond, replacement_rule in rules.items():
            word = replacement_cond.sub(replacement_rule, word)

    if '[' not in word or ']' not in word:
        word = ROOT.sub(r'[\1/RT]', word)
    return word


def annotate_morphemes(input_dir, output_dir, path_to_filename):
    with open(os.path.join(input_dir, path_to_filename), 'r', encoding='utf-8') as f1, \
            open(os.path.join(output_dir, path_to_filename), 'w', encoding='utf-8') as f2:
        for line in f1.readlines():
            t = tuple(eval(line.strip()))
            if t[-1] in 'S A V ADV'.split() and '-' in t[0]:
                if t[-1] in 'S V ADV'.split():
                    for w in t[0].split('-'):
                        index = None
                        if re.search(r'([.,?!…]+)', w):
                            index = re.search(r'([.,?!…]+)', w).start()
                        t_new = (w[:index], t[-1])
                        f2.write(str((apply_rules(t_new), t[-1])))
                        f2.write('\n')

                        if index:
                            t_new = (w[index:], 'NONLEX')
                            f2.write(str(t_new))
                            f2.write('\n')
                            index = None

                        f2.flush()
                else:
                    t_new = (''.join(t[0].split('-')), t[-1])
                    f2.write(str((apply_rules(t_new), t[-1])))
                    f2.write('\n')
                    f2.flush()
            else:
                index = None
                w, pos = t
                if re.search(r'([.,?!…]+)', w):
                    index = re.search(r'([.,?!…]+)', w).start()

                t_new = (apply_rules((w[:index], pos)), t[-1]) if t[-1] not in EXCEPTED_POS else t
                f2.write(str(t_new))
                f2.write('\n')

                if index:
                    t_new = (w[index:], 'NONLEX')
                    f2.write(str(t_new))
                    f2.write('\n')
                    index = None

                f2.flush()


def main(input_dir, output_dir):
    for f in os.listdir(input_dir):
        annotate_morphemes(input_dir, output_dir, f)


if __name__ == '__main__':
    INPUT_DIR = '../../resources/corpora/output'
    OUTPUT_DIR = '../../resources/corpora/annotated'
    main(INPUT_DIR, OUTPUT_DIR)
