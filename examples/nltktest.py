import nltk
from nltk.corpus import treebank
import numpy
from nltk.tree import *
#import nltk.draw.tree.TreeView

from nltk.tree import Tree
from nltk.draw.tree import TreeView
import os, glob


sentence = """At eight o'clock on Thursday morning. Arthur didn't feel very good."""
tokens = nltk.word_tokenize(sentence)
print tokens
#['At', 'eight', "o'clock", 'on', 'Thursday', 'morning',
#'Arthur', 'did', "n't", 'feel', 'very', 'good', '.']
tagged = nltk.pos_tag(tokens)
print tagged[0:6]
#[('At', 'IN'), ('eight', 'CD'), ("o'clock", 'JJ'), ('on', 'IN'),
#('Thursday', 'NNP'), ('morning', 'NN')]

entities = nltk.chunk.ne_chunk(tagged)
print entities
#Tree('S', [('At', 'IN'), ('eight', 'CD'), ("o'clock", 'JJ'),
 #          ('on', 'IN'), ('Thursday', 'NNP'), ('morning', 'NN'),
  #     Tree('PERSON', [('Arthur', 'NNP')]),
   #        ('did', 'VBD'), ("n't", 'RB'), ('feel', 'VB'),
    #       ('very', 'RB'), ('good', 'JJ'), ('.', '.')])
#Display a parse tree:

t = treebank.parsed_sents('wsj_0001.mrg')[0]
t.draw()
#parser= nltk 
#print(tree.pformat_latex_qtree())
#t.pretty_print()


#t = Tree.fromstring(t)#'(S (NP this tree) (VP (V is) (AdjP pretty)))')
TreeView(t)._cframe.print_to_file('output.ps')


os.system('convert output.ps output.png')
