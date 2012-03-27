import urllib2
import json 

whitelist = ['netflix_genre', 'film', 'book', 'music', 'food', 'writer',
             'radio', 'linguist', 'language']

class FreebaseDisambiguator(object):
    def disambiguate(self, text):
        text = urllib2.quote(text)
        url = "https://www.googleapis.com/freebase/v1/search?query="+text+"&key=AIzaSyA3sM2HSS_zg92Gu3kDG7gC-5QwCL2DjT8&limit=2"
        print url
        req = urllib2.Request(url)
        r = urllib2.urlopen(req)
        json_response = json.loads(r.read())
        print json.dumps(json_response, sort_keys=True, indent=4)
        filtered = filter_relevant_results(json_response["result"])
        if filtered:
            return filtered[0]
        else:
            return None

def filter_relevant_results(results):
    good_results = []
    for result in results:
        if is_good(result):
            good_results.append(result["name"])
    return good_results

def is_good(result):
    if result['score'] < 20:
        return False
    if "notable" in result:
        notable_name = result['notable']['name'].lower()
        path = result['notable']['id']
        path = path.split("/")
        for wl in whitelist:
            if wl in path or wl in notable_name:
                return True
    return False
            

def test():
    diser = FreebaseDisambiguator()
    print diser.disambiguate('nirvana')

if __name__ == '__main__':
    test()
