def normalize_grammar(g):
    """
    :param g: grammar (dict of dict of count)
    :return: normalized grammar (dict of dict of probability)
    """
    for pos in g.keys():
        count = sum(g[pos].values())
        for key in g[pos].keys():
            g[pos][key] /= count
    return g

def remove_unit_grammar(grammar):
    """
    :param grammar: grammar (dict of dict of count)
    :return: grammar with no unary rule
    """
    still_unit = False
    for pos in grammar:
        for key in list(grammar[pos]):
            if len(key)==1:
                proba = grammar[pos].pop(key)
                for new_key in list(grammar.get(key[0], {})):
                    grammar[pos][new_key] = grammar[pos].get(new_key, 0)
                    grammar[pos][new_key] = grammar[pos][new_key] + proba*grammar[key[0]][new_key]
                still_unit = True
    return grammar, still_unit

def invert_grammar(g):
    """
    :param g: grammar (from parent to children to probability)
    :return: grammar (from children to parent to probability
    """
    g_inv = {}
    for w, dic in g.items():
        for pos, number in dic.items():
            g_inv[pos] = g_inv.get(pos, {})
            g_inv[pos][w] = number
    return g_inv