from topia.termextract import extract
from test_text import text

class TopiaChunker(object):

    def chunk(self, text):
        output = []
        extractor = extract.TermExtractor()
        for tup in sorted(extractor(text)):
            output.append(tup[0])
        return output

def test():
    chunker = TopiaChunker()
    print chunker.chunk(text)

if __name__ == "__main__":
    test()
