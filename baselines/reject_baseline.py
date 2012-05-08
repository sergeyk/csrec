# reject baseline - always rejecting is not too bad (~15% error on small testset)
from mpi.mpi_imports import *

def reject_baseline_test_predictionerror(data, allow_rejects=True):
  if not allow_rejects:
    return 0.0
  nones = 0
  N = data.get_nsamples()
  for i in range(N):
    cs = data.get_sample(i)
    if cs.get_winner()==None:
      nones += 1
  accuracy = nones / float(N)
  return accuracy
  
def reject_baseline_test_predictionerror_mpi(data, allow_rejects=True):
  if not allow_rejects:
    return 0.0
  nones = 0
  N = data.get_nsamples()
  for i in range(comm_rank, N, comm_size):
    cs = data.get_sample(i)
    if cs.get_winner()==None:
      nones += 1
  safebarrier(comm)
  nones = comm.allreduce(nones)    
  accuracy = nones / float(N)
  return accuracy  
  

  
def reject_baseline_test_meannormalizedwinnerrank(data, allow_rejects=True):
  if not allow_rejects:
    # then we simply have random baseline here, too
    return 0.5
  sumnrank = 0.0
  N = data.get_nsamples()
  for i in range(N):
    competitorset = data.get_sample(i)
    true = competitorset.get_winner()
    if true==None:
      nrank = 0
    else:
      n = len(competitorset.get_surferlist()) + 1 # all candidates + rejectcandidate
      nrank = float(n)/(2*float(n-1)) # Tim thinks it works out like this mathematically
    sumnrank += nrank
    
  meannrank= sumnrank/float(N)  
  return meannrank
  
  
def reject_baseline_test_meannormalizedwinnerrank_mpi(data, allow_rejects=True):
  if not allow_rejects:
    # then we simply have random baseline here, too
    return 0.5
  sumnrank = 0.0
  N = data.get_nsamples()
  for i in range(comm_rank, N, comm_size):
    competitorset = data.get_sample(i)
    true = competitorset.get_winner()
    if true==None:
      nrank = 0
    else:
      n = len(competitorset.get_surferlist()) + 1 # all candidates + rejectcandidate
      nrank = float(n)/(2*float(n-1)) # Tim thinks it works out like this mathematically
    sumnrank += nrank
  
  safebarrier(comm)
  sumnrank = comm.allreduce(sumnrank)   
  meannrank= sumnrank/float(N)  
  return meannrank
  
