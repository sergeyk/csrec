from topia.termextract import extract

class TopiaChunker(object):

    def chunk(self, text):
        output = []
        extractor = extract.TermExtractor()
        for tup in sorted(extractor(text)):
            output.append(tup[0])
        return output

def test():
    from testing.test_text import text
    chunker = TopiaChunker()
    print chunker.chunk(text)

if __name__ == "__main__":
    test()
