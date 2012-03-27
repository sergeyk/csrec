import chunkers.csv_chunker as cc
import chunkers.bagged_chunker as bc
import recognizers.wiki_disambiguator as wd
import recognizers.freebase_disambiguator as fd
from util import chunk_cleanser
import util.chunk_cleanser

class NamedEntityExtractor(object):
    def __init__(self):
        self.chunker = cc.CSVChunker()
        self.disambiguator = fd.FreebaseDisambiguator()
        self.deep_chunker = bc.BaggedChunker()
        self.num_passes = 0

    def extract(self, text, chunker = None):
        if not chunker:
            chunker = self.chunker
        residuals_lst = []
        print 'extracting named entities...'
        output = set([])
        chunks = chunker.chunk(text)
        #chunks = chunk_cleanser.clean(chunks)
        print 'recognizing...'
        for chunk in chunks:
            print chunk, '-->',
            disambed = self.disambiguator.disambiguate(chunk)
            if disambed:
                print disambed
                output.add(disambed)
            else:
                residuals_lst.append(chunk)
        self.num_passes += 1
        if self.num_passes == 1:
            for residual in residuals_lst:
                additional = self.extract(residual, self.deep_chunker)
                [output.add(x) for x in additional]
        output = sorted(list(output))
        return output


def test():
    from testing.test_text import text
    extractor = NamedEntityExtractor()
    print extractor.extract(text) 
        
if __name__ == "__main__":
    test()
