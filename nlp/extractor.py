import bagged_chunker
import wiki_disambiguator, freebase_disambiguator
import chunk_cleanser
from test_text import text

class Extractor(object):
    def __init__(self):
        self.chunker = bagged_chunker.BaggedChunker()
        self.disambiguator = freebase_disambiguator.FreebaseDisambiguator()
        
    def extract(self, text):
        output = set([])
        chunks = self.chunker.chunk(text)
        chunks = chunk_cleanser.clean(chunks)
        for chunk in chunks:
            print chunk, '-->',
            disambed = self.disambiguator.disambiguate(chunk)
            if disambed:
                print disambed
                output.add(disambed)
            else:
                print ''
        output = sorted(list(output))
        return output


def test():
    extractor = Extractor()
    print extractor.extract(text) 
        
if __name__ == "__main__":
    test()
