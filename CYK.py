from nltk.tree import Tree
from grammar_utils import *
import pickle

print('loading grammar and lexicon...')
lexicon_norm = pickle.load(open( "lexicon.p", "rb" ))
grammar = pickle.load(open( "grammar.p", "rb" ))
grammar_inv = invert_grammar(grammar)
print('Done !')

# CYK with unary rules : possible to recover the "real" tree

# these two functions handle a variation of CYK, compatible with unary rule. This allows to recover the "true" tree.
def _add_unary_tab_once(dico):
    still_unit = False
    for pos_from in list(dico.keys()):
        pos_from = (pos_from,)
        for pos_to in list(grammar_inv.get(pos_from, {})):
            if grammar[pos_to][pos_from]*dico[pos_from[0]][0] > dico.get(pos_to, [0])[0]:
                dico[pos_to] = [grammar[pos_to][pos_from]*dico[pos_from[0]][0], pos_from[0]]
                still_unit = True
    return still_unit

def add_every_unary(dico):
    again = True
    while again:
        again = _add_unary_tab_once(dico)

# create first line of the table used by the algorithm
def first_non_terminaux_from_words(s):
    non_term_list = []
    for w in s:
        wdic = lexicon_norm[w]
        nwdic = {k: [v] for (k, v) in wdic.items()}
        add_every_unary(nwdic)
        sum_norm = sum(val[0] for val in nwdic.values())
        for pos in nwdic.keys():
            nwdic[pos][0] = nwdic[pos][0] / sum_norm
        non_term_list.append(nwdic)
    return non_term_list

# for one cell, which cell couples should it visit to update its value
def generate_couple(j, i):
    return [[k, i, j - 1 - k, i + 1 + k] for k in range(j)]

#construct the table cell by cell
def iter_cyk(wlistlist):
    pos_list = []
    for i in range(len(wlistlist[-1]) - 1):
        liste_couple = generate_couple(len(wlistlist), i)
        new_dic = {}
        for couple in liste_couple:
            dic_g = wlistlist[couple[0]][couple[1]]
            dic_d = wlistlist[couple[2]][couple[3]]
            for pos1, v1 in dic_g.items():
                for pos2, v2 in dic_d.items():
                    # inutile maintenant#
                    if not isinstance(v1, float):
                        v1 = v1[0]
                    if not isinstance(v2, float):
                        v2 = v2[0]
                    ### ###
                    for pos_father, proba_trans in grammar_inv.get((pos1, pos2), {}).items():
                        current_proba = new_dic.get(pos_father, [0])[0]
                        if proba_trans * v1 * v2 > current_proba:
                            # on a trouvé un meilleur chemin pour pos_father
                            new_dic[pos_father] = [proba_trans * v1 * v2, pos1, pos2, couple]
        # Handling unary rules
        add_every_unary(new_dic)

        pos_list.append(new_dic)

    return pos_list

# performs the algorithm
def cyk(s):
    """
    :param s: a list of tokens
    :return: a list of list of dictionary, which represent the table of CYK
    """
    l = [first_non_terminaux_from_words(s)]
    while len(l[-1]) > 1:
        l.append(iter_cyk(l))
    return l

#
def _create_sub_tree(cyk_list, pos, coordinates, s):
    """
    Auxiliary function of _tree_from_cyk
    """
    if len(cyk_list[coordinates[0]][coordinates[1]][pos]) == 1:
        # on a atteint une feuille
        return Tree(pos, [Tree(s[coordinates[1]], [])])
    if len(cyk_list[coordinates[0]][coordinates[1]][pos]) == 2:
        # unary rule
        npos = cyk_list[coordinates[0]][coordinates[1]][pos][1]
        return Tree(pos, [_create_sub_tree(cyk_list, npos, coordinates, s)])
    pos1 = cyk_list[coordinates[0]][coordinates[1]][pos][1]
    pos2 = cyk_list[coordinates[0]][coordinates[1]][pos][2]
    coordinates1 = cyk_list[coordinates[0]][coordinates[1]][pos][3][:2]
    coordinates2 = cyk_list[coordinates[0]][coordinates[1]][pos][3][2:]
    return Tree(pos,
                [_create_sub_tree(cyk_list, pos1, coordinates1, s), _create_sub_tree(cyk_list, pos2, coordinates2, s)])


def _tree_from_cyk(cyk_list, s):
    """
    Auxilliary function of tree_from_sentence
    """
    if cyk_list[-1][0].get('SENT', [0])[0] == 0:
        print("The sentence is not in the grammar")
        return Tree('not', [Tree('in', []), Tree('grammar', [])])
    else:
        return _create_sub_tree(cyk_list, 'SENT', [len(cyk_list) - 1, 0], s)


def tree_from_sentence(s):
    """
    :param s: sentence (list of tokens)
    :return: parsing tree
    """
    return _tree_from_cyk(cyk(s), s)