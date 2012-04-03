import os
import cPickle
merged_interest_dct = {}
merged_accepted_pairs = []

for file_name in os.listdir(os.getcwd()):
    if 'id_interest_dct' in file_name:
        id_interest_dct = cPickle.load(open(file_name, 'rb'))
        for k, v in id_interest_dct.iteritems():
            if k not in merged_interest_dct:
                merged_interest_dct[k] = v
        print 'added %s, merged_interest_dct size: %s' % (file_name, len(merged_interest_dct))
    if 'accepted_pairs' in file_name:
        accepted_pairs = cPickle.load(open(file_name, 'rb'))
        for pair in accepted_pairs:
            merged_accepted_pairs.append(pair)
        print 'added %s, merged_accepted_pairs size: %s' % (file_name, len(merged_accepted_pairs))

cPickle.dump(merged_accepted_pairs, open('merged_accepted_pairs.pkl', 'wb'))
cPickle.dump(merged_interest_dct, open('merged_interest_dct.pkl', 'wb'))
