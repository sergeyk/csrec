import chunkers.bagged_chunker as bc
import recognizers.wiki_disambiguator as wd
import recognizers.freebase_disambiguator as fd
from util import chunk_cleanser
import util.chunk_cleanser

class NamedEntityExtractor(object):
    def __init__(self):
        self.chunker = bc.BaggedChunker()
        self.disambiguator = fd.FreebaseDisambiguator()
        
    def extract(self, text):
        print 'extracting named entities...'
        output = set([])
        chunks = self.chunker.chunk(text)
        chunks = chunk_cleanser.clean(chunks)
        print 'recognizing...'
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
    from testing.test_text import text
    extractor = NamedEntityExtractor()
    print extractor.extract(text) 
        
if __name__ == "__main__":
    test()
