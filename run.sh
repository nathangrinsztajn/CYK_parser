python3 create_lex_and_grammar.py -p sequoia-corpus+fct.mrg_strict -ps "$1"
python3 main.py -ps "$1" -po "$2"