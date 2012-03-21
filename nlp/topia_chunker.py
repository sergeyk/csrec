from topia.termextract import extract

class TopiaChunker(object):

    def chunk(self, text):
        output = []
        extractor = extract.TermExtractor()
        for tup in sorted(extractor(text)):
            output.append(tup[0])
        return output

def test():
    text = '''
I consider myself a pretty diverse character... I'm a professional wrestler, but I'd take a bullet for WallE. I train like a one-man genocide machine in the gym, but I cried at "Armageddon." I'll head bang to AC/DC, and I'm seriously considering getting a Legend of Zelda tattoo. I'm 420-friendly. I like to party it up with the frat crowd one night, hang out with my Burning Man friends the next, play Halo and World of Warcraft the next, and jam with friends that aren't any younger than 40 the next. My youngest friend is 16, my oldest friend is 66. I'll sing karaoke at the bars, and I'm my friends' collective psychiatrist/shoulder.
'''
    chunker = TopiaChunker()
    print chunker.chunk(text)

if __name__ == "__main__":
    test()
