from CYK import *
import argparse
from tree import *

parser = argparse.ArgumentParser()
parser.add_argument("-ps", "--path_sample", help="path to the text to parse : tokens separated with a space")
parser.add_argument("-po", "--path_out", help="path to the generated parsing")
args = parser.parse_args()


samplepath = args.path_sample
path_out = args.path_out

with open(samplepath, encoding='utf-8') as input_file:
    sample = input_file.readlines()


#puting everything together
def sent_to_parse_sent(s):
    t = tree_from_sentence(s)
    t = debinarize(t)
    return tree_to_string(t)


out_file_test = open(path_out, "w", encoding='utf-8')

for i, line in enumerate(sample):

    if i%5 == 0:
        print("{:d} / {:d}".format(i, len(sample)))

    # write line to output file
    line = line.split(" ")
    parsing = sent_to_parse_sent(line)
    out_file_test.write(parsing)
    out_file_test.write("\n")

out_file_test.close()