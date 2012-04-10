import csrec_paths
import cPickle
from collections import Counter
from scipy.sparse import lil_matrix
import numpy as np
from itertools import izip

def all_pairs(lst):
    if len(lst) == 2:
        return [(lst[0], lst[1])]
    elif len(lst) < 2:
        return []
    pairs = []
    current_element = lst[0]
    for ele in lst:
        pairs.append((current_element, ele))
    return pairs + all_pairs(lst[1:])

def load_data():
    intra_weight = 1
    inter_weight = .1
    interest_id_map = {}
    id_interest_map = {}
    i_dct = cPickle.load(open(csrec_paths.get_proj_root()+'/features/interests/interest_extraction/merged_interest_dct.pkl', 'rb')) 
    a_pairs = cPickle.load(open(csrec_paths.get_proj_root()+'/features/interests/interest_extraction/merged_accepted_pairs.pkl', 'rb'))
    num_uniques = 0
    for k,v in i_dct.iteritems():
        for i in v:
            if i not in interest_id_map:
                id_interest_map[num_uniques] = i
                interest_id_map[i] = num_uniques
                num_uniques += 1
    matrix_size = len(interest_id_map)
    num_appearances = np.zeros(matrix_size)
    interest_matrix = lil_matrix((matrix_size, matrix_size))
    i = 0
    for k,v in i_dct.iteritems():
        if len(v) >= 2:
            pairs = all_pairs(v)
            for pair in pairs:
                i1 = interest_id_map[pair[0]]
                i2 = interest_id_map[pair[1]]
                if i1 != i2:
                    if i1 < i2:
                        first = i1
                        second = i2
                    else:
                        first = i2
                        second = i1
                    num_appearances[first] += intra_weight
                    num_appearances[second] += intra_weight
                    interest_matrix[first, second] += intra_weight
        i += 1
        print "%s/%s intra-profile completed" % (i, len(i_dct))
    cPickle.dump(num_appearances, open('appearances.pkl', 'wb'))
    cPickle.dump(interest_matrix, open('interest_matrix.pkl', 'wb'))
    cPickle.dump(interest_id_map, open('interest_id_map.pkl', 'wb'))
    cPickle.dump(id_interest_map, open('id_interest_map.pkl', 'wb'))

load_data()
