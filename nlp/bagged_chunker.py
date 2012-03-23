import topia_chunker, yql_chunker, nltk_chunker
from test_text import text

class BaggedChunker(object):
    def __init__(self):
        self.chunkers = []
        self.chunkers.append(topia_chunker.TopiaChunker())
        self.chunkers.append(yql_chunker.YQLChunker())
        self.chunkers.append(nltk_chunker.NLTKChunker())
        
    def chunk(self, text):
        all_chunks = set([])
        for chunker in self.chunkers:
            for chunk in chunker.chunk(text):
                all_chunks.add(chunk)
        l = list(all_chunks)
        l = sorted(l)
        return l

def test():
    chunker = BaggedChunker()
    print chunker.chunk(text) 
        
if __name__ == "__main__":
    test()
