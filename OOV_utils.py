import pickle
import numpy as np
from operator import itemgetter

### Levenshtein ###

def levenshtein(s, t, threshold=None):
    """
    d[i,j] = levenshtein(s[:i], t[:j])
    """
    if threshold is None:
        threshold = len(s) + len(t)
    if abs(len(s) - len(t)) > threshold:
        return threshold + 1
    nrows = len(s) + 1
    ncols = len(t) + 1
    d = [[0 for _ in range(ncols)] for _ in range(nrows)]

    for i in range(len(d)):
        d[i][0] = i
    for i in range(ncols):
        d[0][i] = i

    for i in range(1, nrows):
        for j in range(1, ncols):
            d[i][j] = min(d[i - 1][j - 1] + (s[i - 1] != t[j - 1]), d[i - 1][j] + 1, d[i][j - 1] + 1)
    return d[-1][-1]




### Polyglot ###

file = open('polyglot-fr.pkl', 'rb')
words, embeddings = pickle.load(file, encoding='latin1')

# Map words to indices and vice versa
word_id = {w:i for (i, w) in enumerate(words)}
id_word = dict(enumerate(words))

# Normalise embeddings
norms = np.linalg.norm(embeddings, axis=1)
embeddings = embeddings / norms[:, None]

def cosine_nearest(embeddings, word, k=1):
    """Returns the k nearest words"""
    word_index = word_id[word]
    e = embeddings[word_index]
    distances = np.dot(embeddings, e)
    sorted_distances = sorted(enumerate(distances), key=itemgetter(1), reverse=True)
    return ([id_word[sorted_distances[i][0]] for i in range(1, k+1)],
            [sorted_distances[i][1] for i in range(1, k+1)])

#indices allows faster search
indices = {}
for i, w in enumerate(words):
    l = len(w)
    if l not in indices:
        indices[l] = [i]
    else:
        indices[l].append(i)


def find_near(word, k):
    res = []
    l = len(word)
    for i in range(l - k, l + k + 1):
        if not indices[i]:
            continue
        for index in indices[i]:
            w = words[index]
            if levenshtein(w, word, k) <= k:
                res.append(w)
    return res
