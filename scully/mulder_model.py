from collections import Counter
import numpy as np
from stop_words import get_stop_words
from scully.utils import clean_word


STOP_WORDS = get_stop_words('en') + ['']


def create_counts(df):
    pos_counts, neg_counts = Counter(), Counter()
    pos = [txt.strip() for txt in df[df.CHARACTER == 'MULDER'].TEXT.astype(str).values]
    neg = [txt.strip() for txt in df[df.CHARACTER != 'MULDER'].TEXT.astype(str).values]

    pos_counts.update([clean_word(wrd) for txt in pos for wrd in txt.split()
                       if clean_word(wrd) not in STOP_WORDS])
    neg_counts.update([clean_word(wrd) for txt in neg for wrd in txt.split()
                       if clean_word(wrd) not in STOP_WORDS])
    return pos_counts, neg_counts


def create_scoring_engine(p, q, vocab, prior=0.2):
    index_of = {w: i for i, w in enumerate(vocab)}
    K = len(vocab)

    def predict(phrase):
        clean = [clean_word(wrd) for wrd in phrase.split() if clean_word(wrd) in index_of]
        vec = np.zeros(K)
        for w in clean:
            vec[[index_of[w]]] += 1
        b = np.log(prior)
        w = np.sum(np.log(p) * vec + np.log(1 - p) * (1 - vec))
        resp = b + w

        b = np.log(1 - prior)
        w = np.sum(np.log(q) * vec + np.log(1 - p) * (1 - vec))
        not_resp = b + w
        return resp > not_resp

    return predict


def fit_bayes(df):
    pos_counts, neg_counts = create_counts(df)
    vocab = list(set(pos_counts.keys()).union(neg_counts.keys()))
    K = len(vocab)
    pos_total = sum(pos_counts.values())
    neg_total = sum(neg_counts.values())

    p, q = np.zeros(K), np.zeros(K)
    a, b = 1, 9
    for i, w in enumerate(vocab):
        p[i] = (pos_counts[w] + a) / (pos_total + a + b)
        q[i] = (neg_counts[w] + a) / (neg_total + a + b)

    return create_scoring_engine(p, q, vocab)
