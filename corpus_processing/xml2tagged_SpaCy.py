'''
Tokenization, POS tagging and lemmatization using SpaCy.

Input: sentence splitted XML corpus.
Output: tokenized, POS tagged and lemmatized corpus (still not properly vertical, use tagged2vert.py).

SpaCy's .pos_ adds UPOS coarse-grained tags (use .tag for fine-grained POS tagging)
'''

import argparse
from lxml import etree
import spacy
import gc
from pathlib import Path

gc.set_threshold(1000, 15, 15)      # setting higher thresholds for garbage collection, in order to avoid memory peaks

#  loading German model to SpaCy
nlp = spacy.load("de_core_news_lg")


#  define cmd arguments
parser = argparse.ArgumentParser(description="A script for tokenization, lemmatization and POS tagging using SpaCy")
parser.add_argument("corpus", help="the corpus in .xml format to be tagged")
parser.add_argument("-o", "--overwrite", help="(optional) overwriting the old corpus; by default, a new file is created",
                    action="store_true")
args = parser.parse_args()

#  processing arguments
inputCorpus = args.corpus
overwrite = args.overwrite


with open(inputCorpus, 'r+', encoding='utf-8') as file:
    parser = etree.XMLParser(remove_blank_text=True, encoding='utf-8')
    tree = etree.parse(file, parser)
    print("Corpus parsed. Now tagging...")

    counter = 0

    for element in tree.iter():                             # iterate over each tag element
        if element.text is not None:
            doc = nlp(element.text, disable=['parser', 'ner']) # parse the text with SpaCy
            segm = list()                                   # create a list for the single <s> segments

            for w in doc:                                   # iterate over each word in the segment
                if w.text != '\n' and w.text != '\r' and w.text != '\r\n':  # ignore newline characters
                    # building tab-separated line for vert file (token-POS-lemma)
                    # (use w.tag for fine-grained POS tagging)
                    segm.append(f"""{w.text}\t{w.pos_}\t{w.lemma_}""")

                    counter += 1
                    if (counter/1000).is_integer():
                        print("\r", "%i out of approx 200358000 tokens tagged (%.2f%%)"
                              % (counter, counter/200358000*100))

            element.text = "\n".join(segm)

if overwrite:
    tree.write(inputCorpus, encoding="utf-8")

else:  # if overwrite == False (default)
    filename_old = Path(inputCorpus).stem
    filename_new = filename_old + "_taggedSpaCy.xml"
    tree.write(filename_new, encoding="utf-8")


print("Tokens written: ", counter)
print("Done")



