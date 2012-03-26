from testing.test_text import text
from util import chunk_cleanser

class NgramChunker(object):
    def chunk(self, text):
        text = chunk_cleanser.remove_punctuation(text)
        print text
        all_chunks = set([])
        word_lst = text.split()
        all_chunks.add(word_lst[0])
        for i in range(1,len(word_lst)):
            all_chunks.add(word_lst[i])
            all_chunks.add(word_lst[i-1]+' '+word_lst[i])
        return all_chunks

def test():
    chunker = NgramChunker()
    print chunker.chunk(text) 
        
if __name__ == "__main__":
    test()
