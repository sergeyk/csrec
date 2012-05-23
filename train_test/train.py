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
from competitor_sets.Sqler import *
from features.user_features import FeatureGetter
from math import sqrt
import random
import os
import os.path
import numpy as np
from mpi.mpi_imports import *
import time 
import MySQLdb as mdb
import csrec_paths

try:
    import cPickle as pickle
except:
    import pickle
    
LOOK_AHEAD_LENGTH = 10000
RON_MODE = (os.path.exists('/home/ron'))

def test_meannormalizedwinnerrank(fg, sgd, data, verbose=False): 
  sumnrank = 0.0
  N = data.get_nsamples()
  
  indices = range(comm_rank, N, comm_size)
  update_lookahead_cnt = 0  
  req_ids = data.get_req_ids_for_samples(indices[0:LOOK_AHEAD_LENGTH])
  fg.upt_out_prod_get(req_ids)
  
  for i in indices:
    update_lookahead_cnt += 1
    if update_lookahead_cnt == LOOK_AHEAD_LENGTH:
      req_ids = data.get_req_ids_for_samples(indices[i:i+LOOK_AHEAD_LENGTH])
      fg.upt_out_prod_get(req_ids)
      update_lookahead_cnt = 0
      
    competitorset = data.get_sample(i)
    cand, scores = sgd.rank(competitorset)
    true = competitorset.get_winner()
    if verbose:
      print "Correct %d - Candidates %d - Scores %f"%(true,cand,scores)
    nrank = cand.index(true) / float(len(cand)-1) # len-1 because we have rank 0..n-1
    #if len(cand)>2:
    #  print "from meanNrank eval"
    #  print true, cand, cand.index(true), nrank, sumnrank
    sumnrank += nrank
    
  safebarrier(comm)
  sumnrank = comm.allreduce(sumnrank)
  meannrank= sumnrank/float(N)  
  return meannrank


def run(cfg): 
  lambdas = cfg.lambdas
  memory_for_personalized_parameters = cfg.memory_for_personalized_parameters
  percentage = cfg.train_percentage
  outer_iterations = cfg.outer_iterations
  nepoches = cfg.nepoches
  alpha = cfg.alpha
  beta = cfg.beta
  verbose = cfg.verbose
  personalization = cfg.personalization
  rhostsize = cfg.rhostsize
  just_winning_sets = cfg.just_winning_sets
  testing = cfg.testing
  dirname = cfg.train_dirname
 
  if comm_rank == 0:
    print "using lambdas:", lambdas
  fg = FeatureGetter()
  if cfg.god_mode:
      featuredimension = 1
  else: 
      featuredimension = fg.get_dimension()
  get_feature_function = fg.get_features
  sq = get_sqler()
  overallnum_sets = sq.get_num_compsets('train')
  num_sets = int(overallnum_sets*percentage)

  for i in range(2,comm_size+2,3):
    if comm_rank==i or comm_rank==i-1 or comm_rank==i-2:
      print ("Machine %d/%d - Start loading %s competitorsets for TRAIN"
             % (comm_rank+1,comm_size, num_sets))
      t0 = time.time()
      cs_train = CompetitorSetCollection(num_sets=num_sets, mode = 'train')
      t1 = time.time()
      print "Machine %d/%d - Finished loading the competitorsets for TRAIN."%(comm_rank,comm_size)
      print "Loading competitorsets took %s."%(t1-t0)
 
    safebarrier(comm)
  
  # sleeping so that we dont kill database
  sec = comm_rank
  print "machine %d is sleeping for %d sec."%(comm_rank,sec)
  time.sleep(sec)

  trainerrors = np.zeros((len(lambdas),len(lambdas)))
  testerrors = np.zeros((len(lambdas),len(lambdas)))
  trainmeannrank = np.zeros((len(lambdas),len(lambdas)))
  testmeannrank = np.zeros((len(lambdas),len(lambdas)))
  
  for lw in range(len(lambdas)):
      lambda_winner, lambda_reject = lambdas[lw]
      # Create sgd object   
      if personalization:
        sgd = SGDLearningPersonalized(featuredimension, 
                                      get_feature_function, 
                                      memory_for_personalized_parameters)
      else:
        sgd = SGDLearningRHOSTHASH(featuredimension, 
                                   get_feature_function, 
                                   rhostsize=rhostsize)
        
      N = cs_train.get_nsamples()
      niter = int(N*nepoches)
      
      for outit in range(outer_iterations):
        # for each outer iteration we draw new samples iid per node
        sampleindices = []
        for _ in range(int(nepoches)+1):
          sampleindices += range(N)
        
        random.shuffle(sampleindices)
        update_lookahead_cnt = 0
        req_ids = cs_train.get_req_ids_for_samples(sampleindices[0:LOOK_AHEAD_LENGTH])
        fg.upt_out_prod_get(req_ids)

        for innerit in range(niter):
          i = outit*niter + innerit
          eta_t = 1/sqrt(alpha+i*beta)
          if not i%(niter/5):
              print ("Machine %d/%d - Iterations out: %d/%d - in: %d/%d - eta %f - lambda %f"
                     % (comm_rank, comm_size, outit+1,
                        outer_iterations, innerit+1,niter,eta_t, lambda_winner))

          update_lookahead_cnt += 1
          if update_lookahead_cnt == LOOK_AHEAD_LENGTH:
            req_ids = cs_train.get_req_ids_for_samples(
                sampleindices[innerit:innerit+LOOK_AHEAD_LENGTH])
            fg.upt_out_prod_get(req_ids)
            update_lookahead_cnt = 0
          
          # draw random sample - UPDATE: now first get a random permutation, then do it            
          sampleindex = sampleindices[innerit]
          competitorset = cs_train.get_sample(sampleindex)

          for l in competitorset.get_surferlist():
            assert(l[1] in req_ids)
  
          if verbose and not i%(niter/5) and i>1:
              print ("Iterations \n\tout: %d/%d \n\tin: %d/%d - eta %f - lambda %f"
                     % (outit+1,outer_iterations, innerit+1,niter,eta_t, lambda_winner))
              print "\ttheta", min(sgd.theta), max(sgd.theta)
              print "\tr", sgd.r
              print "\tr_hosts",min(sgd.r_hosts), max(sgd.r_hosts) 
              print "\ttrue", competitorset.get_winner()
              print "\tpredicted", sgd.predict(competitorset)
              print "\tranking", sgd.rank(competitorset)
          sgd.update(competitorset, eta=eta_t, lambda_winner=lambda_winner, 
                     lambda_reject=lambda_reject)

        # Now we aggregate theta(_host), r(_host)
        print ("outer iteration %d/%d: node %d at safebarrier"
               %(outit+1, outer_iterations, comm_rank))
        safebarrier(comm)
        
        if comm_rank == 0:
          print "all nodes arrived and we start allreduce/broadcasting"
        theta = comm.allreduce(sgd.theta)/float(comm_size)
        if comm_rank == 0:
          print "allreduce done for theta"
        if personalization:
          theta_hosts = comm.allreduce(sgd.theta_hosts)/float(comm_size)
          if comm_rank == 0:
            print "allreduce done for theta_hosts"
        r = comm.allreduce(sgd.r)/float(comm_size)
        if comm_rank == 0:
          print "allreduce done for r"
        
        r_hosts = comm.allreduce(sgd.r_hosts)/float(comm_size)
        if comm_rank == 0:
          print "allreduce done for r_hosts"
        
        print 'spreading mean of parameters done!'
        sgd.theta = theta
        if personalization: sgd.theta_hosts = theta_hosts
        sgd.r = r
        sgd.r_hosts = r_hosts
        
      print 'done with training' 
        
      # Store the parameters to /tscratch/tmp/csrec
      if comm_rank == 0:
          if os.path.exists('/tscratch'):
            if not os.path.exists(dirname):
              os.makedirs(dirname)
          filename = ('parameters_lwin_%f_lrej_%f_testing_%d_personalized_%d_numsets_%d_outerit_%d_nepoches_%d.pkl'
                      % (lambda_winner, lambda_reject, 
                         testing, personalization, 
                         num_sets, outer_iterations,nepoches))
          if not RON_MODE:
              os.system('chmod -R 777 '+dirname)
          if personalization:
              pickle.dump( (sgd.theta, sgd.theta_hosts, sgd.r, sgd.r_hosts), open( dirname+filename, "wb" ) )
          else:
              pickle.dump( (sgd.theta, sgd.r, sgd.r_hosts), open( dirname+filename, "wb" ) )
          print "Stored params at " + dirname+filename  
      return filename
     
if __name__=='__main__':
    import load_config
    t_start = time.time()
    run(load_config.cfg)
    print 'run completed in %s sec' % (time.time() - t_start)
