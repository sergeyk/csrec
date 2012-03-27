from nltk.corpus import wordnet as wn
from nltk.metrics import distance
import difflib

def sim(chunk1, chunk2):
    if len(chunk1.split()) == 1 and len(chunk2.split()) == 1:
        return nltk_sim(chunk1, chunk2)
    else:
        return levenshtein(chunk1, chunk2)
    #print seq_match(chunk1, chunk2)

def levenshtein(chunk1, chunk2):
    longest_len = max(len(chunk1), len(chunk2))
    return (1-distance.edit_distance(chunk1, chunk2)/float(longest_len))

def seq_match(chunk1, chunk2):
    s = difflib.SequenceMatcher(None, chunk1, chunk2)
    return s.ratio()

def nltk_sim(chunk1, chunk2):
    chunk1_syn = set(wn.synsets(chunk1))
    chunk2_syn = set(wn.synsets(chunk2))
    if chunk1_syn.intersection(chunk2_syn):
        return 1
    else:
        return 0

if __name__ == '__main__':
    print sim('swimming', 'swim')
