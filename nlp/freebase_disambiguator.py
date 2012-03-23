import urllib2
import json 
from test_text import text

whitelist = ['activity', 'interests', 'hobby', 'netflix_genre', 'film', 'book', 'music']

class FreebaseDisambiguator(object):
    def disambiguate(self, text):
        text = urllib2.quote(text)
        url = "https://www.googleapis.com/freebase/v1/search?query="+text+"&indent=true&limit=2&mql_output={%22name%22:%20null,%22id%22:%20null,%22type%22:%20[],%22/common/topic/notable_for%22:%20{}}"
        req = urllib2.Request(url)
        r = urllib2.urlopen(req)
        json_response = json.loads(r.read())
 #       print json.dumps(json_response, sort_keys=True, indent=4)
        filtered = filter_relevant_results(json_response["result"])
        if filtered:
            return filtered[0]

def filter_relevant_results(results):
    good_results = []
    for result in results:
        if is_good(result):
            good_results.append(result["name"])
    return good_results

def is_good(result):
    for t in result["type"]:
        path = t.split("/")
        for wl in whitelist:
            if wl in path:
                return True
    return False
            

def test():
    diser = FreebaseDisambiguator()
    print diser.disambiguate('hiking')

if __name__ == '__main__':
    test()
