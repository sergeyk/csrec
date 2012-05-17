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
from learning.gradientdescent_personalization import SGDLearningPersonalized
from learning.gradientdescent import SGDLearning
from learning.gradientdescent_rhosthash import SGDLearningRHOSTHASH
from competitor_sets.competitor_sets import CompetitorSetCollection
from competitor_sets.Sqler import Sqler
from features.user_features import FeatureGetter
from math import sqrt
import random
import os
import os.path
import numpy as np
from mpi.mpi_imports import *
import time 
import MySQLdb as mdb
from baselines.reject_baseline import *
from baselines.random_baseline import *
from baselines.singlefeature_baseline import *
RON_MODE = (os.path.exists('/home/ron'))

try:
    import cPickle as pickle
except:
    import pickle
    
LOOK_AHEAD_LENGTH = 10000

def test_predictionerror(fg, sgd, data, allow_rejects=True):
# computes predictionacc or error (getting it exactly right or not) 
  errors = 0
  truenones = 0
  prednones = 0
  N = data.get_nsamples()
  
  indices = range(comm_rank, N, comm_size) 
  update_lookahead_cnt = 0  
  req_ids = data.get_req_ids_for_samples(indices[0:LOOK_AHEAD_LENGTH])
  fg.upt_out_prod_get(req_ids)

  for idx, i in enumerate(indices):
    
    if update_lookahead_cnt == LOOK_AHEAD_LENGTH-2:
      req_ids = data.get_req_ids_for_samples(indices[idx:idx+LOOK_AHEAD_LENGTH+2])
      fg.upt_out_prod_get(req_ids)
      update_lookahead_cnt = 0
    else:
      update_lookahead_cnt += 1
    
    competitorset = data.get_sample(i)
    for l in competitorset.get_surferlist():
      #print l[1]
      try:
        assert(l[1] in fg.outer_product_getter.outer_products.keys())
      except:
        # it is not yet in there! so load by the grace of god!
        fg.outer_product_getter.unsafe_create_outer_prods_from_req_ids(l[1])
    try:
      pred = sgd.predict(competitorset, testingphase=False, allow_rejects=allow_rejects)
    except:
        if not RON_MODE:
            from IPython import embed
            embed()
    true = competitorset.get_winner()
    #if true:
    #  print 'prediction', pred
    #  print 'true val', true
        
    errors += (pred!=true)
    truenones += (true==None)
    prednones += (pred==None)
    
  safebarrier(comm)
  
  errors = comm.allreduce(errors)
  truenones = comm.allreduce(truenones)
  prednones = comm.allreduce(prednones)
    
  errorrate = errors/float(N)  
  truenonerate = truenones/float(N)  
  prednonerate = prednones/float(N) 
  return errorrate, truenonerate, prednonerate


def test_meannormalizedwinnerrank(fg, sgd, data, allow_rejects=True): 
  sumnrank = 0.0
  N = data.get_nsamples()
  
  indices = range(comm_rank, N, comm_size)
  update_lookahead_cnt = 0  
  req_ids = data.get_req_ids_for_samples(indices[0:LOOK_AHEAD_LENGTH])
  fg.upt_out_prod_get(req_ids)
  
  for idx, i in enumerate(indices):
    
    if update_lookahead_cnt == LOOK_AHEAD_LENGTH-2:
      req_ids = data.get_req_ids_for_samples(indices[idx:idx+LOOK_AHEAD_LENGTH+2])
      fg.upt_out_prod_get(req_ids)
      update_lookahead_cnt = 0
    else:
      update_lookahead_cnt += 1
      
    competitorset = data.get_sample(i)
    for l in competitorset.get_surferlist():
      #print l[1]
      try:
        assert(l[1] in fg.outer_product_getter.outer_products.keys())
      except:
        # it is not yet in there! so load by the grace of god!
        fg.outer_product_getter.unsafe_create_outer_prods_from_req_ids(l[1])
    cand, scores = sgd.rank(competitorset, allow_rejects=allow_rejects)
    true = competitorset.get_winner()
    if not allow_rejects and true==None: continue #TODO remove, this is bug
    if len(cand)==1:
      nrank = 0.0
    else:
      nrank = cand.index(true) / float(len(cand)-1) # len-1 because we have rank 0..n-1
    #if len(cand)>2:
    #  print "from meanNrank eval"
    #  print true, cand, cand.index(true), nrank, sumnrank
    sumnrank += nrank
    
  safebarrier(comm)
  sumnrank = comm.allreduce(sumnrank)
  meannrank= sumnrank/float(N)  
  return meannrank


def run():
  # parameters for which learning parameters to use
  personalization = False
  testing = False
  lambda_winner = 0.1
  lambda_reject = 1.0
  num_sets = 1000000
  outer_iterations = 10
  nepoches = 0.05
  
  # load parameters from file (only rank 0)
  if comm_rank == 0:
    dirname = '/tscratch/tmp/csrec/'        
    filename = 'parameters_lwin_%f_lrej_%f_testing_%d_personalized_%d_numsets_%d_outerit_%d_nepoches_%d.pkl'%(lambda_winner, lambda_reject, testing, personalization, num_sets, outer_iterations,nepoches)
    #filename = 'parameters_lwin_0.000100_lrej_0.000100_testing_0_personalized_0_numsets_10000_outerit_10_nepoches_0.pkl' # TODO remove
    filename = 'parameters_lwin_0.001000_lrej_0.001000_testing_0_personalized_0_numsets_100000_outerit_10_nepoches_0.pkl'
    4
    print filename
    if RON_MODE:
        dirname = '/home/ron/csrec/params/'
        filename = 'parameters_lwin_0.100000_lrej_0.100000_testing_0_personalized_0_numsets_500000_outerit_2_nepoches_0.pkl'


    if personalization:
      theta, theta_hosts, r, r_hosts = pickle.load( open( dirname+filename, "rb" ) ) 
    else:
      theta, r, r_hosts = pickle.load( open( dirname+filename, "rb" ) )
    print "Loaded params from " + dirname+filename
  else:
    theta = None
    r = None
    r_hosts = None
    theta_hosts = None   
  
  #from IPython import embed
  #embed()
    
 
  theta = comm.bcast(theta, root=0)
  r = comm.bcast(r, root=0)
  r_hosts = comm.bcast(r_hosts, root=0)
  if personalization:
    theta_hosts = comm.bcast(theta_hosts, root=0)
    
  # create SGD object with those params
  fg = FeatureGetter(False)
  featuredimension = fg.get_dimension()
  get_feature_function = fg.get_features
  memory_for_personalized_parameters = 500
  if personalization:
    sgd = SGDLearningPersonalized(featuredimension, get_feature_function, memory_for_personalized_parameters, theta=theta, r=r, r_hosts=r_hosts, theta_hosts=theta_hosts) # featdim +1 iff cheating
  else:
    #sgd = SGDLearning(featuredimension, get_feature_function, theta=theta, r=r, r_hosts=r_hosts) # without personalization/hashing, faster
    sgd = SGDLearningRHOSTHASH(featuredimension, get_feature_function, theta=theta, r=r, r_hosts=r_hosts)
  
  #print sgd
  
  # load ALL test data
  num_sets = 'max' # 'max' or 10000 -> if max, everybody should have same testset
  for i in range(2,comm_size+2,3):
    if comm_rank==i or comm_rank==i-1 or comm_rank==i-2:
      print "Machine %d/%d - Start loading the competitorsets for TEST"%(comm_rank,comm_size)
      cs_test = CompetitorSetCollection(num_sets=num_sets, mode='test_win')
      
    safebarrier(comm)
  
  baseline = False
  allow_rejects = True
  # let every machine do part of it
  if baseline:
      rejectaccuracy = reject_baseline_test_predictionerror_mpi(cs_test, allow_rejects=allow_rejects)
      rejectmeannrank = reject_baseline_test_meannormalizedwinnerrank_mpi(cs_test, allow_rejects=allow_rejects)
      randomaccuracy = random_baseline_test_predictionerror_mpi(cs_test, allow_rejects=allow_rejects)
      randommeannrank = 0.5
      if comm_rank == 0:
        print "Baselines"
        print "REJECT accuracy:", rejectaccuracy
        print "RANDOM accuracy:", randomaccuracy
        print "REJECT meannrank:", rejectmeannrank
        print "RANDOM meannrank:", randommeannrank  
        
      # do single feature baseline for all features
      features, thresholds = get_features_and_thresholds()
      for featureidx in range(6):
        sgfeataccuracy = singlefeature_baseline_test_predictionerror_mpi(cs_test, features, thresholds, featureidx=featureidx, allow_rejects=allow_rejects)
        sgfeatmeannrank = singlefeature_baseline_test_meannormalizedwinnerrank_mpi(cs_test, features, thresholds, featureidx=featureidx, allow_rejects=allow_rejects)
        if comm_rank == 0:
          print "Baselines"
          print "SGFEAT accuracy - featidx %d : %f"%(featureidx, sgfeataccuracy)
          print "SGFEAT meannrank - featidx %d : %f"%(featureidx, sgfeatmeannrank) 
        
         
  else:
    errorrate, truenonerate, prednonerate = test_predictionerror(fg, sgd, cs_test, allow_rejects=allow_rejects)
    meannrank = test_meannormalizedwinnerrank(fg, sgd, cs_test, allow_rejects=allow_rejects)
    if comm_rank == 0:
      print "[TEST] Errorrate: %f"%(errorrate)
      print "TrueNone-Rate: %f -> error: %f"%(truenonerate, 1.0 - truenonerate)
      print "PredNone-Rate: %f"%(prednonerate)
      print "MEANNRANK: %f"%(meannrank)
  

     
     
if __name__=='__main__':
  run()