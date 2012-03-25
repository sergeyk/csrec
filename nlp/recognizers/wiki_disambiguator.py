import urllib2
import json 

class WikiDisambiguator(object):
    def disambiguate(self, text):
        text = urllib2.quote(text)
        url = "http://en.wikipedia.org/w/api.php?action=opensearch&search=%s&limit=10&namespace=0&format=json"
        query_url = url % (text)
        req = urllib2.Request(query_url)
        r = urllib2.urlopen(req)
        json_response = json.loads(r.read())
        potential = json_response[1]
        if potential:
            return potential[0]
        else:
            return None

def test():
    diser = WikiDisambiguator()
    print diser.disambiguate('Hiking')

if __name__ == '__main__':
    test()
