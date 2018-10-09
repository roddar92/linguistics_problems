import os
import re
import sys
from collections import Counter


STATES = ['AFX', 'RT', 'IFX', 'SFX', 'END', 'PSFX']
ALL_EXCLUDE_BRACKETS = r'([^\[\]]+)'
ANNOT = r'\[' + ALL_EXCLUDE_BRACKETS + r'/(' + r'|'.join(STATES) + r')\]'
ANNOT_PATTERN = re.compile(ANNOT, re.IGNORECASE)


def annot2label(input_dir, output_dir):
    def write_statistics_over_file(all_pairs_count, labels_count, unique_count, filename=None, descr=sys.stdout):
        if not filename:
            descr.write('All processed: lines - {}, labels - {}, unique words - {}'.format(
                all_pairs_count, labels_count, unique_count
            ))
            descr.write('\n')
        else:
            out_descr.write('{}: Processed all {} lines and labels - {}, unique words - {}'.format(
                filename, all_pairs_count, labels_count, len(unique_counter)))
            out_descr.write('\n')

    def write_pos_statistics(pos_tags_counter, descr=sys.stdout):
        descr.write('ALL POS TAGS:')
        descr.write('\n')
        for pos, count in pos_tags_counter.most_common():
            descr.write('{} - {}'.format(pos, count))
            descr.write('\n')

    out_descr = open(os.path.join(output_dir, 'label_statistics.txt'), 'w', encoding='utf-8')
    whole_pairs_count, whole_labels_count = 0, 0
    whole_pos_tags_counter = Counter()
    whole_unique_counter = Counter()

    for f in os.listdir(input_dir):
        input_file = os.path.join(input_dir, f)
        output_file = os.path.join(output_dir, f)
        with open(input_file, 'r', encoding='utf-8') as fin, \
                open(output_file, 'w', encoding='utf-8') as fout:

            all_pairs_count, labels_count = 0, 0
            pos_tags_counter = Counter()
            unique_counter = Counter()

            for line in fin.readlines():
                try:
                    word, pos = tuple(eval(line.strip()))
                    res = []
                    for elem in ANNOT_PATTERN.finditer(word):
                        morph, morph_type = elem.group(1), elem.group(2)
                        res += ['{}-{}'.format(morph, morph_type)]
                    if res:
                        fout.write(','.join(res) + '\t' + pos)
                        fout.write('\n')
                        unique_counter[word] += 1
                        labels_count += 1
                    pos_tags_counter[pos] += 1
                    all_pairs_count += 1
                except:
                    print(line)
            fout.flush()

            write_statistics_over_file(all_pairs_count, labels_count,
                                       len(unique_counter), descr=out_descr, filename=input_file)
            write_pos_statistics(pos_tags_counter, descr=out_descr)
            out_descr.write('\n')
            out_descr.flush()

            whole_pos_tags_counter.update(pos_tags_counter)
            whole_unique_counter.update(unique_counter)
            whole_pairs_count += all_pairs_count
            whole_labels_count += labels_count

    write_statistics_over_file(whole_pairs_count, whole_labels_count,
                               len(whole_unique_counter), descr=out_descr)
    write_pos_statistics(whole_pos_tags_counter, descr=out_descr)
    out_descr.flush()

    if out_descr:
        out_descr.close()


if __name__ == '__main__':
    INPUT_DIR = '../../resources/corpora/annotated'
    OUTPUT_DIR = '../../resources/corpora/true_labels'
    annot2label(INPUT_DIR, OUTPUT_DIR)
