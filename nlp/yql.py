import urllib
import xml.parsers.expat

url = 'http://search.yahooapis.com/ContentAnalysisService/V1/termExtraction'
appid = 'YahooDemo'
context2 = '''
Well Interests...I'm interested in a lot but the most is probably obligatory because I don't find time for them. Current Interests of mine are TRAVELLING - to explore the world(at the moment the United States), improving my english skills and I recently started to learn spanish, meeting new people, reading(can't stop reading if I find a good book), concerts, coffee ( I guess I found the right place to stay in Seattle as a coffee-addicted person), tennis,snowboarding, meeting friends for a beer and interesting conversations or having a lazy movie night
'''
context = '''
I consider myself a pretty diverse character... I'm a professional wrestler, but I'd take a bullet for WallE. I train like a one-man genocide machine in the gym, but I cried at "Armageddon." I'll head bang to AC/DC, and I'm seriously considering getting a Legend of Zelda tattoo. I'm 420-friendly. I like to party it up with the frat crowd one night, hang out with my Burning Man friends the next, play Halo and World of Warcraft the next, and jam with friends that aren't any younger than 40 the next. My youngest friend is 16, my oldest friend is 66. I'll sing karaoke at the bars, and I'm my friends' collective psychiatrist/shoulder.
'''
query = 'madonna'

params = urllib.urlencode({
	'appid': appid,
	'context': context,
	'query': query
})

data = urllib.urlopen(url, params).read()

# 3 handler functions
def start_element(name, attrs):
    print 'Start element:', name, attrs
def end_element(name):
    print 'End element:', name
def char_data(data):
    print str(data)

p = xml.parsers.expat.ParserCreate()

p.CharacterDataHandler = char_data

print context
print ''
print '====YQL====='
print p.Parse(data)

print '\n'

print '====topia===='

from topia.termextract import extract
extractor = extract.TermExtractor()
for tup in sorted(extractor(context)):
    print tup[0]
