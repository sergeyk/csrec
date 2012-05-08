import cPickle
from scipy.sparse import lil_matrix
import numpy as np

appearances = cPickle.load(open('appearances.pkl', 'rb'))
i_matrix = cPickle.load(open('interest_matrix.pkl', 'rb'))
print appearances

nz_x, nz_y = i_matrix.nonzero()

count = 0
for i in range(len(nz_x)):
    count += 1

    x = nz_x[i]
    y = nz_y[i]
    
    i_matrix[x, y] *= 1/2*\
        (1/float(appearances[x]) + \
             1/float(appearances[y]))
    
    print '%s/%s normalized' % (count, len(nz_x))

cPickle.dump(i_matrix, open('norm_interest_matrix.pkl', 'wb'))
