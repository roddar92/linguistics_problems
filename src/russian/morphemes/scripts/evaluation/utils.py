import os
import re
import sys
from collections import Counter, defaultdict


STATES = ['AFX', 'RT', 'IFX', 'SFX', 'END', 'PSFX', 'IMPSFX', 'SFXEND', 'RTEND', 'AFXEND']
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

    def write_tag_statistics(tags_counter, descr=sys.stdout):
        descr.write('ALL TAGS:')
        descr.write('\n')
        if isinstance(tags_counter, Counter):
            for tag, count in tags_counter.most_common():
                descr.write('{} - {}'.format(tag, count))
                descr.write('\n')
        else:
            for tag, vals in tags_counter.items():
                descr.write('{} - {}'.format(tag, len(vals)))
                descr.write('\n')
                if len(vals) < 100:
                    descr.write('{} - {}'.format(tag, vals))
                    descr.write('\n')

    out_descr = open(os.path.join(output_dir, 'label_statistics.txt'), 'w', encoding='utf-8')
    whole_pairs_count, whole_labels_count = 0, 0
    whole_pos_tags_counter = Counter()
    whole_unique_counter = Counter()
    whole_mopheme_type_counter = Counter()
    whole_mopheme_counter = defaultdict(set)

    for f in os.listdir(input_dir):
        input_file = os.path.join(input_dir, f)
        output_file = os.path.join(output_dir, f)
        with open(input_file, 'r', encoding='utf-8') as fin, \
                open(output_file, 'w', encoding='utf-8') as fout:

            all_pairs_count, labels_count = 0, 0
            pos_tags_counter = Counter()
            unique_counter = Counter()
            mopheme_type_counter = Counter()
            mopheme_counter = defaultdict(set)

            for line in fin.readlines():
                try:
                    word, pos = tuple(eval(line.strip()))
                    res = []
                    for elem in ANNOT_PATTERN.finditer(word):
                        morph, morph_type = elem.group(1), elem.group(2)
                        res += ['{}-{}'.format(morph, morph_type)]
                        mopheme_type_counter[morph_type] += 1
                        if morph_type in ['RT', 'RTEND']:
                            mopheme_counter[morph_type].add(morph)
                        else:
                            for p in pos.split(','):
                                mopheme_counter[(morph_type, p.strip())].add(morph)
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
            write_tag_statistics(pos_tags_counter, descr=out_descr)
            out_descr.write('\n')
            write_tag_statistics(mopheme_type_counter, descr=out_descr)
            out_descr.write('\n')
            write_tag_statistics(mopheme_counter, descr=out_descr)
            out_descr.write('\n')
            out_descr.flush()

            whole_pos_tags_counter.update(pos_tags_counter)
            whole_unique_counter.update(unique_counter)
            whole_mopheme_type_counter.update(mopheme_type_counter)
            for morph_tup in mopheme_counter:
                whole_mopheme_counter[morph_tup].update(mopheme_counter[morph_tup])
            whole_pairs_count += all_pairs_count
            whole_labels_count += labels_count

    write_statistics_over_file(whole_pairs_count, whole_labels_count,
                               len(whole_unique_counter), descr=out_descr)
    write_tag_statistics(whole_pos_tags_counter, descr=out_descr)
    out_descr.write('\n')
    write_tag_statistics(whole_mopheme_type_counter, descr=out_descr)
    out_descr.write('\n')
    write_tag_statistics(whole_mopheme_counter, descr=out_descr)
    out_descr.flush()

    if out_descr:
        out_descr.close()


if __name__ == '__main__':
    INPUT_DIR = '../../resources/corpora/annot_ready'
    OUTPUT_DIR = '../../resources/corpora/true_labels'
    annot2label(INPUT_DIR, OUTPUT_DIR)
