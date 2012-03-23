# Natural Language Toolkit: code_classifier_chunker
import nltk
from nltk.corpus import conll2000
import cPickle
from nltk.draw import tree
from test_text import text

class ConsecutiveNPChunkTagger(nltk.TaggerI): # [_consec-chunk-tagger]

    def __init__(self, train_sents):
        train_set = []
        for tagged_sent in train_sents:
            untagged_sent = nltk.tag.untag(tagged_sent)
            history = []
            for i, (word, tag) in enumerate(tagged_sent):
                featureset = self.npchunk_features(untagged_sent, i, history) # [_consec-use-fe]
                train_set.append( (featureset, tag) )
                history.append(tag)
        self.classifier = nltk.MaxentClassifier.train( # [_consec-use-maxent]
            train_set, algorithm='megam', trace=0)

    def tag(self, sentence):
        history = []
        for i, word in enumerate(sentence):
            featureset = self.npchunk_features(sentence, i, history)
            tag = self.classifier.classify(featureset)
            history.append(tag)
        return zip(sentence, history)

    def npchunk_features(self, sentence, i, history):
        word, pos = sentence[i]
        if i == 0:
            prevword, prevpos = "<START>", "<START>"
        else:
            prevword, prevpos = sentence[i-1]
        if i == len(sentence)-1:
            nextword, nextpos = "<END>", "<END>"
        else:
            nextword, nextpos = sentence[i+1]
        return {"pos": pos,
                "word": word,
                "prevpos": prevpos,
                "nextpos": nextpos, 
                "prevpos+pos": "%s+%s" % (prevpos, pos),  
                "pos+nextpos": "%s+%s" % (pos, nextpos),
                "tags-since-dt": self.tags_since_dt(sentence, i)}  

    def tags_since_dt(self, sentence, i):
        tags = set()
        for word, pos in sentence[:i]:
            if pos == 'DT':
                tags = set()
            else:
                tags.add(pos)
        return '+'.join(sorted(tags))


class ConsecutiveNPChunker(nltk.ChunkParserI): # [_consec-chunker]
    def __init__(self, train_sents):
        tagged_sents = [[((w,t),c) for (w,t,c) in
                         nltk.chunk.tree2conlltags(sent)]
                        for sent in train_sents]
        self.tagger = ConsecutiveNPChunkTagger(tagged_sents)

    def parse(self, sentence):
        # Input: tagged sentence
        tagged_sents = self.tagger.tag(sentence)
        conlltags = [(w,t,c) for ((w,t),c) in tagged_sents]
        return nltk.chunk.conlltags2tree(conlltags)


class NLTKChunker(object):

    def __init__(self):
        try:
            self.unigram_chunker = cPickle.load(open('chunker.pkl', 'r'))
        except (EOFError, IOError):
            train_sents = conll2000.chunked_sents('train.txt', chunk_types=['NP'])
            unigram_chunker = ConsecutiveNPChunker(train_sents)
            f = open('chunker.pkl', 'wb')
            cPickle.dump(unigram_chunker, f, -1)

    def chunk_backup(self, text):
        token_text = nltk.word_tokenize(text)
        tagged_text = nltk.pos_tag(token_text)
        chunk_tree = self.unigram_chunker.parse(tagged_text)
        output = []
        for subtree in chunk_tree.subtrees(filter=lambda t: t.node == 'NP'):
            output.append(" ".join([x[0] for x in subtree.leaves()]))
        return output


    def chunk(self, text):
        token_text = nltk.word_tokenize(text)
        tagged_text = nltk.pos_tag(token_text)
        chunk_tree = nltk.ne_chunk(tagged_text)
        output = []
        for subtree in chunk_tree.subtrees(filter=lambda t: t.node != 'S'):
            output.append(" ".join([x[0] for x in subtree.leaves()]))
        return output

def test():
    chunker = NLTKChunker()
    print chunker.chunk(text)

if __name__ == "__main__":
    test()
