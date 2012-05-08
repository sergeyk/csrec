# single feature baseline - similar to CS system
from mpi.mpi_imports import *
try:
    import cPickle as pickle
except:
    import pickle
    
# can assume dict[userID] -> (x,y,z,..)
# and thresholds

def argsort(seq):
    # http://stackoverflow.com/questions/3071415/efficient-method-to-calculate-the-rank-vector-of-a-list-in-python
    return sorted(range(len(seq)), key=seq.__getitem__, reverse=True)

def get_features_and_thresholds():
  # load pickle
  filename = "foo"
  features, thresholds = pickle.load( open(filename, "rb" ) )
  return features, thresholds

def singlefeature_baseline_test_predictionerror(data, featureidx=0):
  features, thresholds = get_features_and_thresholds()
  correct = 0
  N = data.get_nsamples()
  for i in range(N):
    cs = data.get_sample(i)
    userIDlist = list(zip(*cs.get_surferlist())[0])
    scores = [features[userID][featureidx] for userID in userIDlist]
    idx = argsort(scores)
    sortedscores = [scores[i] for i in idx]
    sortedcandidates = [userIDlist[i] for i in idx]
    pred = sortedcandidates[0] if sortedscores[0]>thesholds[featureidx] else None
    if cs.get_winner()==pred:
      correct += 1
  accuracy = correct / float(N)
  return accuracy
  
 
def singlefeature_baseline_test_predictionerror_mpi(data, featureidx=0):
  features, thresholds = get_features_and_thresholds()
  correct = 0
  N = data.get_nsamples()
  for i in range(comm_rank, N, comm_size):
    cs = data.get_sample(i)
    userIDlist = list(zip(*cs.get_surferlist())[0])
    scores = [features[userID][featureidx] for userID in userIDlist]
    idx = argsort(scores)
    sortedscores = [scores[i] for i in idx]
    sortedcandidates = [userIDlist[i] for i in idx]
    pred = sortedcandidates[0] if sortedscores[0]>thesholds[featureidx] else None
    if cs.get_winner()==pred:
      correct += 1
  correct = comm.allreduce(correct)
  accuracy = correct / float(N)
  return accuracy
  

def singlefeature_baseline_test_meannormalizedwinnerrank(data, featureidx=0):
  features, thresholds = get_features_and_thresholds()
  sumnrank = 0.0
  N = data.get_nsamples()
  for i in range(N):
    cs = data.get_sample(i)
    true = competitorset.get_winner()
    userIDlist = list(zip(*cs.get_surferlist())[0])
    scores = [features[userID][featureidx] for userID in userIDlist]
    # add None with threshold
    userIDlist.append(None)
    scores.append(threshold[featureidx])
    idx = argsort(scores)
    sortedscores = [scores[i] for i in idx]
    sortedcandidates = [userIDlist[i] for i in idx]
    nrank = sortedcandidates.index(true) / float(len(sortedcandidates)-1) # len-1 because we have rank 0..n-1
    sumnrank += nrank
  meannrank= sumnrank/float(N)  
  return meannrank
  
  
def singlefeature_baseline_test_meannormalizedwinnerrank_mpi(data, featureidx=0):
  features, thresholds = get_features_and_thresholds()
  sumnrank = 0.0
  N = data.get_nsamples()
  for i in range(N):
    cs = data.get_sample(i)
    true = competitorset.get_winner()
    userIDlist = list(zip(*cs.get_surferlist())[0])
    scores = [features[userID][featureidx] for userID in userIDlist]
    # add None with threshold
    userIDlist.append(None)
    scores.append(threshold[featureidx])
    idx = argsort(scores)
    sortedscores = [scores[i] for i in idx]
    sortedcandidates = [userIDlist[i] for i in idx]
    nrank = sortedcandidates.index(true) / float(len(sortedcandidates)-1) # len-1 because we have rank 0..n-1
    sumnrank += nrank
  sumnrank = comm.allreduce(sumnrank)  
  meannrank= sumnrank/float(N)  
  return meannrank
  
