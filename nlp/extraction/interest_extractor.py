import chunkers.ngram_chunker as nc
import recognizers.freebase_interest_disambiguator as fd
from util import chunk_cleanser
import util.chunk_cleanser

class InterestExtractor(object):
    def __init__(self):
        self.chunker = nc.NgramChunker()
        self.disambiguator = fd.FreebaseInterestDisambiguator()
        
    def extract(self, text):
        print 'extracting named entities...'
        output = set([])
        chunks = self.chunker.chunk(text)
        chunks = chunk_cleanser.clean(chunks)
        print 'recognizing...'
        for chunk in chunks:
            disambed = self.disambiguator.disambiguate(chunk)
            if disambed:
                print disambed
                output.add(disambed)
        output = sorted(list(output))
        return output


def test():
    from testing.test_text import text
    extractor = InterestExtractor()
    print extractor.extract(text) 
        
if __name__ == "__main__":
    test()
