'''
Parallelize the SGD
Roadmap:
# determine % of dataset for each node
# for iter (?!)
  # per node:
    # draw % of data at random
    # sgd object (first iter: params random, then use params of last iteration)
    # do NITER iterations of learning
    # sgd_theta, sgd_r, sgd_rh

    # construct mean over params:
      - on node 0, comm.reduce
    
# return params
'''

from mpi4py import MPI
from mpi.safebarrier import safebarrier
from competitor_sets.competitor_sets import CompetitorSetCollection
from competitor_sets.Sqler import Sqler
comm = MPI.COMM_WORLD
comm_rank = comm.Get_rank()
comm_size = comm.Get_size()

percentage = 0.3
outer_iterations = 100
sq = Sqler()
print sq.get_num_compsets()

for _ in range(outer_iterations):
  dataobject = CompetitorSetCollection(testing=False,validation=False)
