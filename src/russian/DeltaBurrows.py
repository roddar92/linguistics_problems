import numpy as np
import sys


from nltk import word_tokenize, sent_tokenize

from pathlib import Path
import zipfile

from collections import defaultdict, Counter
from itertools import combinations

from tqdm import tqdm


import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import squareform
from scipy.stats import shapiro


class DeltaMethod:
    def __init__(self):
        self.tokens = Counter()
        self.token_to_doc = defaultdict(Counter)
        self.token_means = {}
        self.token_stds = {}
        self.total_tokens = {}

        self.filenames = None
        self.alpha = 0.05

    def build_corpus(self, path_to_corpus, topn_words):
        self.tokens.clear()
        self.token_to_doc.clear()
        self.token_means.clear()
        self.token_stds.clear()
        self.total_tokens.clear()
        self.filenames = None

        if path_to_corpus.endswith('.zip'):
            texts = self.__read_texts_from_archive(path_to_corpus)
        else:
            corpus_path = Path(path_to_corpus)
            if corpus_path.is_dir():
                texts = self.__read_texts_from_folder(corpus_path)
            else:
                print('Program needs to have a corpus as a ZIP file or a folder!')
                sys.exit(0)

        if texts:
            self.filenames = list(texts.keys())

            for filename, doc in tqdm(texts.items(), total=len(texts), desc='Corpus preprocessing'):
                tokens = self.__preproc(doc)
                self.total_tokens[filename] = len(tokens)
                for token in tokens:
                    self.tokens[token] += 1
                    self.token_to_doc[token][filename] += 1

            k = 0
            print('Selecting TOP-N words..')
            for item in self.tokens.most_common():
                token, _ = item
                freqs = [
                    self.token_to_doc[token][doc_id] / self.total_tokens[doc_id]
                    for doc_id in self.filenames
                ]
                m, s = np.mean(freqs), np.std(freqs)
                if s == 0:
                    continue

                self.token_means[token] = m
                self.token_stds[token] = s
                k += 1
                if k >= topn_words:
                    break

    @staticmethod
    def __read_texts_from_folder(folder_path):
        texts = {}
        for file in Path(folder_path).glob("*.txt"):
            texts[file.name] = file.read_text(encoding="utf-8")
        return texts

    @staticmethod
    def __read_texts_from_archive(zip_path):
        texts = {}
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for filename in zip_ref.namelist():
                if filename.endswith('.txt'):
                    with zip_ref.open(filename) as file:
                        texts[filename] = file.read().decode('utf-8')
        return texts

    @staticmethod
    def __preproc(doc):
        return [
            token.lower()
            for sent in sent_tokenize(doc, language='russian')
            for token in word_tokenize(sent, language='russian')
        ]

    def __z(self, doc_id, token):
        if doc_id not in self.total_tokens or self.total_tokens[doc_id] == 0:
            return 0.0
        if token not in self.token_means or token not in self.token_stds:
            return 0.0

        token_doc_count = self.token_to_doc[token][doc_id] / self.total_tokens[doc_id]
        m, s = self.token_means[token], self.token_stds[token]
        return (token_doc_count - m) / s

    def __calc_cosine(self, u, v):
        u_norm, v_norm = np.linalg.norm(u), np.linalg.norm(v)
        if u_norm == 0 or v_norm == 0:
            cosine = 0.0
        else:
            cosine = np.dot(u, v) / (u_norm * v_norm)
        return cosine

    def __calc_classical_delta(self, u, v):
        return np.mean(np.abs(u - v))

    def __calc_cosine_delta(self, u, v):
        cosine = self.__calc_cosine(u, v)
        return 1 - cosine

    def calculate_delta(self, corpus_path, topn_words=100, method='classic'):
        assert method in ('classic', 'cosine')
        self.build_corpus(corpus_path, topn_words)

        delta_scores = {}
        pairs = list(combinations(self.filenames, 2))
        tokens = list(self.token_means.keys())

        if method == 'classic':
            __func = self.__calc_classical_delta
        else:
            __func = self.__calc_cosine_delta

        for doc1, doc2 in tqdm(pairs, total=len(pairs), desc='Calculate Cosine Delta'):
            u = np.array([self.__z(doc1, token) for token in tokens])
            v = np.array([self.__z(doc2, token) for token in tokens])
            delta_scores[(doc1, doc2)] = __func(u, v)
        return delta_scores

    def calculate_delta_zscores(self, delta_scores):
        if not delta_scores:
            print("Delta distances are not empty. Impossible to compute Delta Z-scores!")
            return {}

        all_distances = list(delta_scores.values())
        _, pval = shapiro(all_distances)
        if pval < self.alpha:
            print("Warning: Deltas are not in Normal distribution. Impossible to compute Z-score.")
            return {pair: 0.0 for pair in delta_scores.keys()}

        mean_delta = np.mean(all_distances)
        std_delta = np.std(all_distances)

        if std_delta == 0:
            print("Warning: Standard derivation is 0. Impossible to compute Z-score.")
            return {pair: 0.0 for pair in delta_scores.keys()}

        z_deltas = {}
        for pair, dist in delta_scores.items():
            z_score = (dist - mean_delta) / std_delta
            z_deltas[pair] = z_score

        return z_deltas

    def print_confident_pairs(self, delta_scores, threshold=-1.5):
        sorted_pairs = sorted(self.calculate_delta_zscores(delta_scores).items(), key=lambda x: x[1])

        print(f"Pairs with the most similar confidence (Z-score < {threshold})")
        found = False
        for (doc1, doc2), z_val in sorted_pairs:
            if z_val <= threshold:
                print(
                    f"Pair: [{doc1}] <-> [{doc2}] | Z-Delta = {z_val:.3f} (High similarity)"
                )
                found = True

        if not found:
            print("Not found any pair.")

    def predict_author_confidence(self, anonymous_doc, delta_scores, verbose=0):
        author_distances = {}

        for (doc1, doc2), dist in delta_scores.items():
            if doc1 == anonymous_doc:
                author_distances[doc2] = dist
            elif doc2 == anonymous_doc:
                author_distances[doc1] = dist

        if not author_distances:
            return f"Document {anonymous_doc} was not found."

        authors = list(author_distances.keys())
        distances = np.array(list(author_distances.values()))

        scaled_distances = -distances

        exp_dist = np.exp(scaled_distances - np.max(scaled_distances))
        probabilities = exp_dist / exp_dist.sum()

        results = sorted(
            zip(authors, probabilities), key=lambda x: x[1], reverse=True
        )

        if verbose:
            print(f"Attribution results for '{anonymous_doc}':")
            for author, prob in results:
                print(f" - {author}: Confidence {prob:.2%}")

        return results

    def plot_dendrogram(self, delta_scores, figsize=(10, 7)):
        if not delta_scores:
            print("The dictionary with Delta distances is empty!")
            return

        doc_list = self.filenames
        n = len(doc_list)
        doc_to_idx = {doc: i for i, doc in enumerate(doc_list)}
        distance_matrix = np.zeros((n, n))

        for (doc1, doc2), dist in delta_scores.items():
            i, j = doc_to_idx[doc1], doc_to_idx[doc2]
            distance_matrix[i, j] = dist
            distance_matrix[j, i] = dist

        condensed_matrix = squareform(distance_matrix)
        Z = linkage(condensed_matrix, method="ward")

        plt.figure(figsize=figsize)
        plt.title("The dendrogram of texts similarity based on Delta Method", fontsize=14)

        dendrogram(
            Z,
            labels=doc_list,
            orientation="left",
            leaf_font_size=10,
        )

        plt.xlabel("Delta")
        plt.tight_layout()
        plt.show()


if __name__ == '__main__':
    dm = DeltaMethod()
    dir_path = './resources/corpus/tolstye.zip'

    # Classical Delta
    deltas = dm.calculate_delta(dir_path, method='classic')

    dm.plot_dendrogram(deltas)
    dm.print_confident_pairs(deltas)
    dm.predict_author_confidence('corpus/Tolstoy_AK_Upyr.txt', deltas, verbose=1)

    # Cosine Delta
    deltas = dm.calculate_delta(dir_path, method='cosine')

    dm.plot_dendrogram(deltas)
    dm.print_confident_pairs(deltas)
    dm.predict_author_confidence('corpus/Tolstoy_AK_Upyr.txt', deltas, verbose=1)
