import urllib
import xml.parsers.expat

class YQLChunker(object):
    def __init__(self):
        self.url = 'http://search.yahooapis.com/ContentAnalysisService/V1/termExtraction'
        self.appid = 'YahooDemo'
        self.buffer = []

    def char_data(self, data):
        self.buffer.append(str(data))
    
    def chunk(self, text):
        self.buffer = []
        params = urllib.urlencode({
                'appid': self.appid,
                'context': text
                })
        data = urllib.urlopen(self.url, params).read()
        p = xml.parsers.expat.ParserCreate()
        p.CharacterDataHandler = self.char_data
        p.Parse(data)
        output = list(self.buffer)
        self.buffer = []
        return output
        # 3 handler functions

def test():
    text = '''
I consider myself a pretty diverse character... I'm a professional wrestler, but I'd take a bullet for WallE. I train like a one-man genocide machine in the gym, but I cried at "Armageddon." I'll head bang to AC/DC, and I'm seriously considering getting a Legend of Zelda tattoo. I'm 420-friendly. I like to party it up with the frat crowd one night, hang out with my Burning Man friends the next, play Halo and World of Warcraft the next, and jam with friends that aren't any younger than 40 the next. My youngest friend is 16, my oldest friend is 66. I'll sing karaoke at the bars, and I'm my friends' collective psychiatrist/shoulder.
'''
    chunker = YQLChunker()
    print chunker.chunk(text)

if __name__ == "__main__":
    test()
