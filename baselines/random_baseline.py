# random baseline - computes expected value of picking the right guy (or None)
from mpi.mpi_imports import *

def random_baseline_test_predictionerror(data, allow_rejects=True):
  sumacc = 0.0
  N = data.get_nsamples()
  for i in range(N):
    cs = data.get_sample(i)
    noptions = allow_rejects + len(cs.get_surferlist())
    sumacc += 1 / float(noptions)
  accuracy = sumacc / float(N)
  return accuracy

def random_baseline_test_predictionerror_mpi(data, allow_rejects=True):
  sumacc = 0.0
  N = data.get_nsamples()
  for i in range(comm_rank, N, comm_size):
    cs = data.get_sample(i)
    noptions = allow_rejects + len(cs.get_surferlist())
    sumacc += 1 / float(noptions)
  safebarrier(comm)
  sumacc = comm.allreduce(sumacc)
  accuracy = sumacc / float(N)
  return accuracy

def random_baseline_test_meannormalizedwinnerrank():
  return 0.5 # Tim thinks it works out like this mathematically
