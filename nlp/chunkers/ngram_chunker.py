from testing.test_text import text
from util import chunk_cleanser

class NgramChunker(object):
    def chunk(self, text):
        text = chunk_cleanser.remove_punctuation(text)
        all_chunks = []
        word_lst = text.split()
        if word_lst:
            all_chunks.append(word_lst[0])
            for i in range(1,len(word_lst)):
                all_chunks.append(word_lst[i])
                all_chunks.append(word_lst[i-1]+' '+word_lst[i])
            all_chunks = sorted(all_chunks, key=lambda x: len(x.split()), reverse=True)
        return all_chunks

def test():
    chunker = NgramChunker()
    print chunker.chunk(text)
        
if __name__ == "__main__":
    test()
