from testing.test_text import text
from util import chunk_cleanser
import re

class CSVChunker(object):
    def chunk(self, text):
        chunks = []
        segments = re.split('[\n\r]+', text)
        for s in segments:
            comma_separated = s.split(',')
            for chunk in comma_separated:
                words = chunk.split()
                non_colon_words = [w for w in words if ':' not in w]
                chunk = ' '.join(non_colon_words)
                if chunk:
                    chunks.append(chunk)
        return chunks
                

def test():
    chunker = CSVChunker()
    print chunker.chunk(text) 
        
if __name__ == "__main__":
    test()
