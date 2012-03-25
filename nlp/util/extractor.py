import chunkers.bagged_chunker as bc
import recognizers.wiki_disambiguator as wd
import recognizers.freebase_disambiguator as fd
import util.chunk_cleanser

class Extractor(object):
    def __init__(self):
        self.chunker = bc.BaggedChunker()
        self.disambiguator = fd.FreebaseDisambiguator()
        
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
    from testing.test_text import text
    extractor = Extractor()
    print extractor.extract(text) 
        
if __name__ == "__main__":
    test()
