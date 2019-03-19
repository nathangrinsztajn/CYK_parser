from tree import *
from grammar_utils import *
import argparse
from OOV_utils import *


parser = argparse.ArgumentParser()
parser.add_argument("-r", "--rm_unary", help="achieves Chomsky normalization by removing unary rules", action="store_true")
parser.add_argument("-p", "--path_corpus", help="path to the training corpus", default='/Users/anneabeille/Documents/MVA/Speech/parser/sequoia-corpus+fct.mrg_strict')
parser.add_argument("-ps", "--path_sample", help="path to the text to parse")
args = parser.parse_args()
if args.rm_unary:
    print("creating grammar, removing unary rules")
else:
    print('creating grammar, keeping unary rules')

grammar = {}
lexicon = {}

def parcour_tree_fin(t):
    """
    :param t: binarized tree
    :return: fill grammar and lexicon in place
    """
    lab_cur = remove_function(t.label())
    if isinstance(t[0], str):
        lexicon[t[0]] = lexicon.get(t[0], {})
        lexicon[t[0]][lab_cur] = lexicon[t[0]].get(lab_cur, 0) + 1
    else:
        child_t = []
        for child in t:
            child_t.append(remove_function(child.label()))
        child_t = tuple(child_t)
        grammar[lab_cur] = grammar.get(lab_cur, {})
        grammar[lab_cur][child_t] =  grammar[lab_cur].get(child_t, 0)+1
        for child in t:
            parcour_tree_fin(child)


# Load dataset
# there are 3099 lines in the whole dataset

# fill the path
filepath = args.path_corpus
samplepath = args.path_sample

with open(filepath, encoding='utf-8') as input_file:
    lines = input_file.readlines()
    train = lines[int(len(lines) * 0.1):int(len(lines) * 0.9)]
    #test = lines[int(len(lines) * 0.9):]
    #val = lines[:int(len(lines) * 0.1)]

with open(samplepath, encoding='utf-8') as input_file:
    sample = input_file.readlines()

sample = [line[:-1].split(" ") for line in sample]

for line in train:
    t = Tree.fromstring(line[2: -2])
    t = binarize_tree(t)
    parcour_tree_fin(t)

grammar = normalize_grammar(grammar)

if args.rm_unary:
    still_unit_in_g = True
    while still_unit_in_g:
        grammar, still_unit_in_g = remove_unit_grammar(grammar)
    # need to renormalize
    grammar = normalize_grammar(grammar)



### add needed words in lexicon ###

print('grammar and lexicon loaded from training corpus')
print('starting inference of unknown words in the sample to parse.... (this can be quite long)')

def _create_from_lex(word, wnear, weight=1):
    """
    Auxilliary function of create_lex_entry
    """
    for pos, count in lexicon.get(wnear, {}).items():
        lexicon[word] = lexicon.get(word, {})
        lexicon[word][pos] = lexicon[word].get(pos, 0) + weight * count


def create_lex_entry(word, indice_sentence=1, k_lev=1, d_emb=5):
    """
    :param word: word to add in the lexicon
    :param indice_sentence: index of the word in the sentence (important for upper letters)
    :param k_lev: distance of levenshtein to consider
    :param d_emb: how many neighboors should be kept in the embedding
    :return: inplace, add the word in the lexicon based on the tags of its neighboors
    """
    if indice_sentence > 0 and (word[0].upper() == word[0]) and (word[0].lower() != word[0]):
        lexicon[word] = {'NPP': 1, 'ADJ': 0.05, 'NC': 0.05}
        # print('a')
        # print(lexicon[word])

    elif '_' in word:
        lexicon[word] = {'P': 341, 'PRO': 29, 'ADV': 336, 'DET': 102, 'CS': 97,
                         'CC': 36, 'P+D': 98, 'V': 7, 'ADJ': 5, 'ET': 1, 'CLS': 9, 'NC': 4}
    else:
        near_word_lev = find_near(word, k_lev)
        for w in near_word_lev:
            if w in lexicon:
                _create_from_lex(word, w)
            else:
                w_emb_list, w_weight_list = cosine_nearest(embeddings, w, d_emb)
                for index, w_emb in enumerate(w_emb_list):
                    _create_from_lex(word, w_emb, w_weight_list[index])
    if word not in lexicon:  # not a clue of what it might be
        lexicon[word] = {'NC': 1 / 3, 'ADJ': 1 / 3, 'V': 1 / 3}


# add every needed words of the sample
for nline, wlist in enumerate(sample):
    if nline%5 == 0:
        print("{:d} / {:d}".format(nline, len(sample)))
    t = Tree.fromstring(line)
    t = t.pos()
    for i, w in enumerate(wlist):
        if w not in lexicon:
            create_lex_entry(w, indice_sentence=i)


# normalize lexicon and grammar
lexicon_inv = invert_grammar(lexicon)
lexicon_inv = normalize_grammar(lexicon_inv)
lexicon_norm = invert_grammar(lexicon_inv)
grammar_inv = invert_grammar(grammar)

pickle.dump(lexicon_norm, open( "lexicon.p", "wb" ) )
pickle.dump(grammar, open( "grammar.p", "wb" ) )

print('Done !')