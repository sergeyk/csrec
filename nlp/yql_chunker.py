import urllib
import xml.parsers.expat
from test_text import text

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
    chunker = YQLChunker()
    print chunker.chunk(text)

if __name__ == "__main__":
    test()
