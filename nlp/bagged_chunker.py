import topia_chunker, yql_chunker, nltk_chunker

class BaggedChunker(object):
    def __init__(self):
        self.chunkers = []
        self.chunkers.append(topia_chunker.TopiaChunker())
        self.chunkers.append(yql_chunker.YQLChunker())
        self.chunkers.append(nltk_chunker.NLTKChunker())
        
    def chunk(self, text):
        all_chunks = set([])
        for chunker in self.chunkers:
            for chunk in chunker.chunk(text):
                all_chunks.add(chunk)
        l = list(all_chunks)
        l = sorted(l)
        return l

def test():
    text = '''
I consider myself a pretty diverse character... I'm a professional wrestler, but I'd take a bullet for WallE. I train like a one-man genocide machine in the gym, but I cried at "Armageddon." I'll head bang to AC/DC, and I'm seriously considering getting a Legend of Zelda tattoo. I'm 420-friendly. I like to party it up with the frat crowd one night, hang out with my Burning Man friends the next, play Halo and World of Warcraft the next, and jam with friends that aren't any younger than 40 the next. My youngest friend is 16, my oldest friend is 66. I'll sing karaoke at the bars, and I'm my friends' collective psychiatrist/shoulder.
'''

    chunker = BaggedChunker()
    print chunker.chunk(text) 
        
if __name__ == "__main__":
    test()
