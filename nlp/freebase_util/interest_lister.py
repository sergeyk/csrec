import csv
import cPickle

target_types = ('/interests/interest',
                '/sports/sport',
                '/interests/hobby',
                '/music/instrument')
                

print 'stage 1: building the frame'

try:
    interests = cPickle.load(open('interests_frame.pkl', 'r'))
except (EOFError, IOError):
    reader = csv.reader(open('freebase-datadump-quadruples.tsv', 'rb'), delimiter='\t')
    interests = {}
    for row in reader:
        if row[1] == '/type/object/type' \
                and row[2] in target_types:
            interests[row[0]] = {"names":[]}
            print row[0]
    f = open('interests_frame.pkl', 'wb')
    print 'found %s interests' % (len(interests))
    cPickle.dump(interests, f, -1)

print 'stage 2: filling the frame'

reader = csv.reader(open('freebase-datadump-quadruples.tsv', 'rb'), delimiter='\t')
for row in reader:
    if (row[1] == '/type/object/name' \
            or row[1] == '/common/topic/alias')\
            and row[2] == '/lang/en' \
            and row[0] in interest:
        interests[row[0]]['names'].append(row[3])
        print row[3]
f = open('named_interests.pkl', 'wb')
cPickle.dump(interests, f, -1)
