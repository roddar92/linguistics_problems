import os

from nltk.tag import pos_tag
from nltk import sent_tokenize, word_tokenize

import nltk
nltk.download('averaged_perceptron_tagger_ru')


def extract_pos_tag(pos_tuple):
    pos = pos_tuple[-1]
    if '=' in pos:
        pos = pos.split('=')[0]
    result = (pos_tuple[0], pos)
    return result


def text_preprocessing(input_dir, output_dir, path_to_filename):
    data = open(os.path.join(input_dir, path_to_filename), 'r', encoding='utf-8').read()
    tokens = [
        word.lower() for sent in sent_tokenize(data) for word in word_tokenize(sent)
    ]
    tokens_with_pos = pos_tag(tokens, lang='rus')
    with open(os.path.join(output_dir, path_to_filename), 'w', encoding='utf-8') as f:
        for token_with_pos in tokens_with_pos:
            f.write(str(extract_pos_tag(token_with_pos)))
            f.write('\n')
            f.flush()


def main(input_dir, output_dir):
    for f in os.listdir(input_dir):
        text_preprocessing(input_dir, output_dir, f)


if __name__ == '__main__':
    INPUT_DIR = '../../resources/corpora/input'
    OUTPUT_DIR = '../../resources/corpora/output'
    main(INPUT_DIR, OUTPUT_DIR)
