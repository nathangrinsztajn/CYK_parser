from nltk.tree import Tree
import re


def remove_function(p):
    """
    :param p: string
    :return: string without functional tags
    """
    return re.sub(r'-[^ ]*', "", p)


def binarize_tree(t):
    """
    :param t: tree
    :return: binarized tree with new nodes
    """
    # child = [binarize_tree(child)]
    if isinstance(t[0], str):
        return t
    if len(t) <= 2:
        return Tree(t.label(), [binarize_tree(child) for child in t])
    else:
        new_pos = ''
        for child in t[1:]:
            new_pos = new_pos + '|' + child.label()
        new_pos = new_pos[1:]
        return Tree(t.label(), [binarize_tree(t[0]), Tree(new_pos, [binarize_tree(child) for child in t[1:]])])


def remove_function_tree(t):
    """
    :param t: tree
    :return: tree withouth functional labels
    """
    if not isinstance(t, str):
        return Tree(remove_function(t.label()), [remove_function_tree(child) for child in t])
    return t

def debinarize(t):
    """
    :param t: binary tree with made-up nodes
    :return: "true" binary tree, with nodes in the initial grammar
    """
    if len(t[0])==0: #leaf
        return t
    if len(t)==1: #une branche
        return Tree(t.label(), [debinarize(t[0])])
    if "|" in t[1].label(): #symbol in grammar
        right_child = debinarize(t[1])
        return Tree(t.label(), [debinarize(t[0])] + [great_child for great_child in right_child ])
    return Tree(t.label(), [debinarize(t[0])] + [debinarize(t[1])])

def bracket_to_list(b):
    """
    :param b: string with parsing format
    :return: list of sentence tokens
    """
    return Tree.fromstring(b).leaves()

def tree_to_string(tree):
    """
    :param tree: the tree to convert
    :return: string in penn treebank format
    """
    if len(tree)==0:
        return tree.label()
    if isinstance(tree, str):
        return tree
    else:
        l = [tree_to_string(child) for child in tree]
        s = '(' + tree.label() + ' '
        for lc in l:
            s = s + lc
        s = s + ')'
        return s