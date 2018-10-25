import os
import re


RT = r'([^\[\]]+)'
ROOT = re.compile(r'(.+)')
NOUN_SUFFIXES = r'(ович|ость|ост(?=([аэеиоуыя]$))|ист|ичн|тель?|ниц|ник|щик|енк|ньк|ушк|ишк|изм|ств|' \
                r'ек|ик|ец|йц|нц|ок|ов|ич|яч|иц|ц|к)'
ADJ_SUFFIXES = r'(ическ|ост(?=н)|ист(?=[а-я])|ичн|тель?|еньк|альн|енк|ньк|ушк|ишк|ичн|изм|ств|' \
                r'ск|йц|нц|чк|оч|ов|чн|ич|зн|ст(?=[а-я])|сн|иц|ив|к)'
PAST_VB_SFX = r'([аяиеыё])(л)'
ENDING = r'(?<![аеиоуыэюя])([аеиоуыэюя])'
ADJ_ENDINGS = r'(ая|ай|ий|ой|ый|ые|ою|ия|ие|ии|ию|ую|ее|ое)'
VERB_ENDINGS = r'([уюаяеи]те?)'
AFFIX = r'(на|не|во[зс]|пере|бе[зс]|пр[иео]|обо?|анти|пред|под|еже|вы|по|ра[зс]|у|о|за|из|до|от|вз)'
NOUN_AFFIX = r'(во[зс]|бе[зс]|пр[иео]|анти|сверх|пред|еже|под|ра[зс]|вз)'

NOUN_REPLACEMENT_RULES = {
    re.compile(r'(?<!^)' + r'(ого|его)$'): r'[\1/END]',
    re.compile(r'(?<!^)' + r'((ом|ам|ем|им|ым)и)$'): r'[\1/END]',
    re.compile(r'(?<!^)(е[ей])$'): r'[\1/SFX]',
    re.compile(r'(?<!^)' + ENDING + r'$'): r'[\1/END]',
    re.compile(r'(?<!^)' + ENDING + r'\['): r'[\1/END][',
    re.compile(r'(?<!^)(ом|ов|ам|ем|им|ым|ах|их|ых|ях)$'): r'[\1/END]',
    re.compile(r'(?<!^)' + r'([йь])$'): r'[\1/RTEND]',
    re.compile(r'(?<!^)(знь)$'): r'[\1/SFX]',
    re.compile(r'(?<!^)([аеёи]нн?|нн?)\['): r'[\1/SFX][',
    re.compile(r'(?<!^)' + NOUN_SUFFIXES + '\['): r'[\1/SFX][',
    re.compile(r'(?<!^)' + NOUN_SUFFIXES + '$'): r'[\1/SFX]',
    re.compile(r'(ен|ов)\['): r'[\1/IFX][',
    re.compile(r'^' + NOUN_AFFIX + r'(?!$)'): r'[\1/AFX]',
    re.compile(r'AFX\](ъ)'): r'AFX][\1/AFXEND]',
    re.compile(r'\]' + RT + r'\['): r'][\1/RT][',
    re.compile(r'^' + RT + r'\['): r'[\1/RT][',
    re.compile(r'\]' + RT + r'$'): r'][\1/RT]'
}


ADJ_REPLACEMENT_RULES = {
    re.compile(r'(?<!^)' + r'(ого|его)$'): r'[\1/END]',
    re.compile(r'(?<!^)' + r'((ом|ам|ем|им|ым)и)$'): r'[\1/END]',
    re.compile(r'(?<!^)(е[ей])$'): r'[\1/SFX]',
    re.compile(r'(?<!^)' + ENDING + r'$'): r'[\1/END]',
    re.compile(r'(?<!^)' + ENDING + r'\['): r'[\1/END][',
    re.compile(r'(?<!^)' + ADJ_ENDINGS + r'$'): r'[\1/END]',
    re.compile(r'(?<!^)(ом|ов|ам|ем|им|ым|ах|их|ых|ях)$'): r'[\1/END]',
    re.compile(r'(?<!^)' + r'([йь])$'): r'[\1/RTEND]',
    re.compile(r'(?<!^)([аеёи]нн?|нн?)\['): r'[\1/SFX][',
    re.compile(r'(?<!^)' + ADJ_SUFFIXES + '\['): r'[\1/SFX][',
    re.compile(r'(?<!^)' + ADJ_SUFFIXES + '$'): r'[\1/SFX]',
    re.compile(r'(?<!^)([уюаяи]щ|ем|им)\['): r'[\1/SFX][',
    re.compile(r'(ен|ов)\['): r'[\1/IFX][',
    re.compile(r'^' + AFFIX + r'(?!$)'): r'[\1/AFX]',
    re.compile(r'AFX\](ъ)'): r'AFX][\1/AFXEND]',
    re.compile(r'\]' + RT + r'\['): r'][\1/RT][',
    re.compile(r'^' + RT + r'\['): r'[\1/RT][',
    re.compile(r'\]' + RT + r'$'): r'][\1/RT]'
}


ADV_REPLACEMENT_RULES = {
    re.compile(r'(?<!^)([аеиоуы])$'): r'[\1/SFX]',
    re.compile(r'(?<!^)(н)\['): r'[\1/SFX][',
    re.compile(r'^' + AFFIX + r'(?!$)'): r'[\1/AFX]',
    re.compile(r'AFX\](ъ)'): r'AFX][\1/AFXEND]',
    re.compile(r'\]' + RT + r'\['): r'][\1/RT][',
    re.compile(r'^' + RT + r'\['): r'[\1/RT][',
    re.compile(r'\]' + RT + r'$'): r'][\1/RT]'
}


PRO_REPLACEMENT_RULES = {
    re.compile(r'(?<!^)([ео](го|й)|и[мх]и?|[аеиоуый])$'): r'[\1/END]',
    re.compile(r'\]' + RT + r'\['): r'][\1/RT][',
    re.compile(r'^' + RT + r'\['): r'[\1/RT][',
    re.compile(r'\]' + RT + r'$'): r'][\1/RT]'
}


VERB_REPLACEMENT_RULES = {
    re.compile(r'(?<!^)' + r'(с[ья])$'): r'[\1/PSFX]',
    re.compile(r'(?<!^)' + VERB_ENDINGS + r'$'): r'[\1/END]',
    re.compile(r'(?<!^)' + VERB_ENDINGS + r'\[(с[ья])'): r'[\1/END][\2',
    re.compile(r'(?<!^)' + ADJ_ENDINGS + r'$'): r'[\1/END]',
    re.compile(r'(?<!^)' + r'([уюаяеи]шь)$'): r'[\1/END]',
    re.compile(r'(?<!^)' + r'([уюаяеи]шь)\[(с[ья])'): r'[\1/END][\2',
    re.compile(r'(?<!^)' + r'(и?т[еь])\['): r'[\1/END][',
    re.compile(r'(?<!^)' + r'(и?т[еь])$'): r'[\1/END]',
    re.compile(r'(?<!^)([аеиоуыэюя])\[ть'): r'[\1/SFX][ть',
    re.compile(r'(?<!^)' + ENDING + r'$'): r'[\1/END]',
    re.compile(r'(?<!^)' + ENDING + r'\['): r'[\1/END][',
    re.compile(r'(?<!^)' + r'([вя])\[сь'): r'[\1/SFX][сь',
    re.compile(r'(?<!^)' + r'([вя])$'): r'[\1/SFX]',
    re.compile(r'(?<!^)([уюаяи]щ|вш|енн|инн|нн)\['): r'[\1/SFX][',
    re.compile(r'(?<!^)(а)\[нн'): r'[\1/SFX][нн',
    re.compile(r'(?<!^)' + PAST_VB_SFX + '\['): r'[\1/SFX][\2/SFX][',
    re.compile(r'(?<!^)' + PAST_VB_SFX + r'$'): r'[\1/SFX][\2/SFX]',
    re.compile(r'(?<!^)([нкш])\['): r'[\1/SFX][',
    re.compile(r'(?<!^)(ем|им)\['): r'[\1/SFX][',
    re.compile(r'(?<!^)(ич)\['): r'[\1/SFX][',
    re.compile(r'^' + AFFIX + r'(?!$)'): r'[\1/AFX]',
    re.compile(r'AFX\](ъ)'): r'AFX][\1/AFXEND]',
    re.compile(r'\]' + RT + r'\['): r'][\1/RT][',
    re.compile(r'^' + RT + r'\['): r'[\1/RT][',
    re.compile(r'\]' + RT + r'$'): r'][\1/RT]'
}


EXCEPTED_POS = ['CONJ', 'PR', 'NONLEX', 'S-PRO', 'ADV-PRO', 'PART', 'PRAEDIC']


def apply_rules(word_tuple):
    def is_long_seq(word):
        return len(word) > 3

    word, pos = word_tuple
    word = re.sub(r'ё', 'е', word)
    rules = NOUN_REPLACEMENT_RULES if pos == 'S' \
        else ADJ_REPLACEMENT_RULES if pos in 'A NUM'.split() \
        else PRO_REPLACEMENT_RULES if pos in 'A-PRO S-PRO'.split() \
        else ADV_REPLACEMENT_RULES if pos == 'ADV' else VERB_REPLACEMENT_RULES
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
                if t[-1] in 'S V ADV'.split() or t[-1] == 'A' and len(set(t[0].split('-'))) == 1:
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
