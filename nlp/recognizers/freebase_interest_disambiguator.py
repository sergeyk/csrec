#!/usr/bin/python
#By Steve Hanov, 2011. Released to the public domain
import time
import sys
import cPickle
import nlp.nlp_paths as paths
from nltk.stem.porter import PorterStemmer
from nltk.stem.lancaster import LancasterStemmer
from nlp.util import chunk_similarity
from nltk.metrics import distance

MOST_COMMON = paths.get_proj_root()+"/util/1000_most_common.pkl";
DICTIONARY = paths.get_proj_root()+"/freebase_util/interest_lst.pkl";
CUSTOM = ['drinking', 'partying', 'wine']
TOP_K_FILTER = 200

# The Trie data structure keeps a set of words, organized with one node for
# each letter. Each node has a branch for each letter that may follow it in the
# set of words.
class TrieNode:
    def __init__(self):
        self.word = None
        self.children = {}

    def insert( self, word ):
        node = self
        for letter in word:
            if letter not in node.children: 
                node.children[letter] = TrieNode()

            node = node.children[letter]

        node.word = word

# The search function returns a list of all words that are less than the given
# maximum distance from the target word
def search(trie, word, maxCost ):

    # build first row
    currentRow = range( len(word) + 1 )

    results = []

    # recursively search each branch of the trie
    for letter in trie.children:
        searchRecursive( trie.children[letter], letter, word, currentRow, 
            results, maxCost )

    return results

# This recursive helper is used by the search function above. It assumes that
# the previousRow has been filled in already.
def searchRecursive( node, letter, word, previousRow, results, maxCost ):

    columns = len( word ) + 1
    currentRow = [ previousRow[0] + 1 ]

    # Build one row for the letter, with a column for each letter in the target
    # word, plus one for the empty string at column 0
    for column in xrange( 1, columns ):

        insertCost = currentRow[column - 1] + 1
        deleteCost = previousRow[column] + 1

        if word[column - 1] != letter:
            replaceCost = previousRow[ column - 1 ] + 1
        else:                
            replaceCost = previousRow[ column - 1 ]

        currentRow.append( min( insertCost, deleteCost, replaceCost ) )

    # if the last entry in the row indicates the optimal cost is less than the
    # maximum cost, and there is a word in this trie node, then add it.
    if currentRow[-1] <= maxCost and node.word != None:
        results.append( (node.word, currentRow[-1] ) )

    # if any entries in the row are less than the maximum cost, then 
    # recursively search each branch of the trie
    if min( currentRow ) <= maxCost:
        for letter in node.children:
            searchRecursive( node.children[letter], letter, word, currentRow, 
                results, maxCost )

class FreebaseInterestDisambiguator(object):
    def __init__(self):
        self.stemmer = LancasterStemmer()
        self.stem_mapping = {}
        self.stemmed_trie = TrieNode()
        self.trie = TrieNode()
        self.singles_lst = []
        self.black_listed_stems = set([])
        loaded = cPickle.load(open(DICTIONARY, 'r'))
        print len(loaded)
        loaded += CUSTOM
        loaded = set(loaded)
        most_common = cPickle.load(open(MOST_COMMON, 'r'))
        for word in most_common:
            self.black_listed_stems.add(self.stem(word))
        #print self.black_listed_stems
        for word in loaded:
            word = word.lower()
            if word not in most_common[:TOP_K_FILTER]:
                self.trie.insert(word)
                stemmed_word = self.stem(word)
                if stemmed_word in self.stem_mapping: 
                    previous = self.stem_mapping[stemmed_word]
                    edist = distance.edit_distance(word, previous)
                    if edist > 2:
                        pass
                    #print 'warning: %s dropped in favor of %s' % (word, previous)
                else:
                    if stemmed_word not in self.black_listed_stems:
                        self.stem_mapping[stemmed_word] = word
                        self.stemmed_trie.insert(stemmed_word)

    def stem(self, text):
        return " ".join([self.stemmer.stem(w) for w in text.split()])

    def nltk_search(self, text):
        for word in self.singles_lst:
            if chunk_similarity.nltk_sim(text, word):
                return word
    
    def stem_leven_search(self, text):
        stemmed_text = self.stem(text)
        result = self.leven_search(stemmed_text, self.stemmed_trie, 1)
        if result:
            return self.stem_mapping[result]

    def leven_search(self, text, trie=None, percent_match=.9):
        max_cost = int((1-percent_match)*len(text))
        results = search(trie, text, max_cost)
        if results:
            results = sorted(results, key=lambda x: x[1])
            return results[0][0]
        else:
            return None

    def disambiguate(self, text):
        text = text.lower()
        first =  self.leven_search(text, self.trie)
        if first:
            return first
        else:
            return self.stem_leven_search(text)

def test():
    from util import chunk_cleanser
    diser = FreebaseInterestDisambiguator() 
    print diser.disambiguate(chunk_cleanser.remove_punctuation('string instruments'))

if __name__ == '__main__':
    test()
