import nlp.chunkers.ngram_chunker as nc
import nlp.recognizers.freebase_interest_disambiguator as fd
from nlp.util import chunk_cleanser
import nlp.util.chunk_cleanser

class InterestExtractor(object):
    def __init__(self):
        self.chunker = nc.NgramChunker()
        self.disambiguator = fd.FreebaseInterestDisambiguator()
        
    def extract(self, text):
        #print 'extracting named entities...'
        output = set([])
        chunks = self.chunker.chunk(text)
        chunks = chunk_cleanser.clean(chunks)
        #print 'recognizing...'
        while len(chunks) > 0:
            chunk = chunks.pop(0)
            disambed = self.disambiguator.disambiguate(chunk)
            if disambed:
                #print chunk, '->', disambed
                output.add(disambed)
                to_remove_lst = chunk.split()
                for r in to_remove_lst:
                    if r in chunks:
                        chunks.remove(r)
            
        output = sorted(list(output))
        return output


def test():
    import sys
    import csv
    import nlp.nlp_paths as nlp_paths
    f = nlp_paths.get_proj_root()+'/testing/test_interest_text'
    extractor = InterestExtractor()
    reader = csv.reader(open(f, 'rb'), delimiter='$')
    i = 0
    desired = int(sys.argv[1])
    for row in reader:
        if len(row)==1:
            i += 1
            if i == desired:
                #print row[0]
                print extractor.extract(row[0]) 
    
if __name__ == "__main__":
    test()
