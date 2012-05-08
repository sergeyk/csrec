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
active_nodes = set([])
threshold = .0006
def filter():
    for i in range(num_nz):
        x = nz_x[i]
        y = nz_y[i]
        sim = i_matrix[x,y]
        if sim > threshold:
            active_nodes.add(x)
            active_nodes.add(y)
            pair = (x, y, sim)
            related.append(pair)
            #print id_interest_map[x], id_interest_map[y], sim
        if i%10000==0:
            print '%s/%s analyzed' % (i, num_nz)
    print len(active_nodes), 'nodes active'
    cPickle.dump(related, open('filtered_edges.pkl', 'wb'))
    cPickle.dump(active_nodes, open('active_nodes.pkl', 'wb'))

def analayze():
    import scipy
    possible_values = []
    for i in range(num_nz):
        x = nz_x[i]
        y = nz_y[i]
        sim = i_matrix[x,y]
        possible_values.append(sim)
        if i%10000==0:
            print '%s/%s analyzed' % (i, num_nz)
    print scipy.stats.mstats.mquantiles(possible_values)
    #print possible_values[:3]
    import matplotlib.pyplot as plt
    gaussian_numbers = possible_values
    plt.hist(gaussian_numbers, bins=10000)
    plt.title('sim')
    xlabel = "Value"
    plt.xlabel(xlabel)
    plt.ylabel("Frequency")
    plt.show()

#analayze()
filter()
