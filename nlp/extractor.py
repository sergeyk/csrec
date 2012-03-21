import bagged_chunker
import wiki_disambiguator

class Extractor(object):
    def __init__(self):
        self.chunker = bagged_chunker.BaggedChunker()
        self.disambiguator = wiki_disambiguator.WikiDisambiguator()
        
    def extract(self, text):
        output = set([])
        chunks = self.chunker.chunk(text)
        for chunk in chunks:
            disambed = self.disambiguator.disambiguate(chunk)
            if disambed:
                print chunk, '-->', disambed
                output.add(disambed)
        output = sorted(list(output))
        return output


def test():
    text = '''
I consider myself a pretty diverse character... I'm a professional wrestler, but I'd take a bullet for WallE. I train like a one-man genocide machine in the gym, but I cried at "Armageddon." I'll head bang to AC/DC, and I'm seriously considering getting a Legend of Zelda tattoo. I'm 420-friendly. I like to party it up with the frat crowd one night, hang out with my Burning Man friends the next, play Halo and World of Warcraft the next, and jam with friends that aren't any younger than 40 the next. My youngest friend is 16, my oldest friend is 66. I'll sing karaoke at the bars, and I'm my friends' collective psychiatrist/shoulder.
'''
    extractor = Extractor()
    print extractor.extract(text) 
        
if __name__ == "__main__":
    test()
