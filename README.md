

CYK-based Parser
=======
The directory contains several files :

 - Test.txt displays examples of the parser, while test_truth.txt display the ground truth. The evalb scoring is given in score.txt


 - **tree.py** : contains several function to handle tree class.
 - **OOV_utils.py** : the module to handle out-of-vocabulary words. Contains the Levenshtein algorithm, and manipulate embeddings from polyglot.
 - **grammar_utils.py** : several functions to manipulate grammars (stored as dict of dict).
 - **create_lex_and_grammar.py** :  take as argument a training corpus and a text to parse, output as pickle files the grammar and the lexicon gotten from the corpus and the OOV.
  One can choose to remove unary rules from the grammar using -r. To create the files :
 `python3 create_lex_and_grammar.py (-r) -p path/to/corpus -ps path/to/text `
 - **CYK.py** : the probabilistic CYK algorithm, with a slight variation to handle unary rules.
 - **main.py** : Once you have created the grammar, parse the text file.
  `python3 main.py -ps path/to/input -po path/to/output`


