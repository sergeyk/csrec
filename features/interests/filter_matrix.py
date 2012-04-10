import cPickle
from scipy.sparse import lil_matrix
import numpy as np
from scipy.stats.mstats import mquantiles
i_matrix = cPickle.load(open('norm_interest_matrix.pkl', 'rb'))
id_interest_map = cPickle.load(open('id_interest_map.pkl', 'rb'))
nz_x, nz_y = i_matrix.nonzero()

count = 0
print i_matrix.mean(axis=0)
print i_matrix.shape
num_nz = len(nz_x)
max_so_far = 0
print id_interest_map[0]
related = []

for i in range(num_nz):
    x = nz_x[i]
    y = nz_y[i]
    sim = i_matrix[x,y]
    active_nodes = set([])
    t_max = max(max_so_far, i_matrix[x,y])
    if t_max != max_so_far:
        max_so_far = t_max
        print max_so_far
        print id_interest_map[x], id_interest_map[y]
    if sim > .001:
        active_nodes.add(x)
        active_nodes.add(y)
        pair = (x, y, sim)
        related.append(pair)
        print id_interest_map[x], id_interest_map[y], sim

cPickle.dump(related, open('filtered_edges.pkl', 'wb'))
cPickle.dump(active_nodes, open('active_nodes.pkl', 'wb'))
