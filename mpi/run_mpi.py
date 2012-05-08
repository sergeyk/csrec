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

try:
    import cPickle as pickle
except:
    import pickle
    
LOOK_AHEAD_LENGTH = 10000

def test_predictionerror(fg, sgd, data):
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
    
    if update_lookahead_cnt == LOOK_AHEAD_LENGTH-1:
      req_ids = data.get_req_ids_for_samples(indices[idx:idx+LOOK_AHEAD_LENGTH+1])
      fg.upt_out_prod_get(req_ids)
      update_lookahead_cnt = 0
    else:
      update_lookahead_cnt += 1    
        
    competitorset = data.get_sample(i)
    for l in competitorset.get_surferlist():
      #print l[1]
      assert(l[1] in req_ids)
    pred = sgd.predict(competitorset, testingphase=False)
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


def run(): 
  lambdas = [(float(sys.argv[1]),float(sys.argv[2]))]
  if comm_rank == 0:
    print "using lambda:", lambdas
 
  memory_for_personalized_parameters = 20 #512.0 # memory in MB if using personalized SGD learning  
  percentage = 0.2 # Dependent on machines in future min:10%, 2nodes->80%
  outer_iterations = 1 #10
  nepoches = 0.0003 #0.05 #10
  alpha = 100.0
  beta = 0.001 #0.01
  #lambda_winner = 0.01
  #lambda_reject = 0.01
  verbose = False
  personalization = False # no hashing -> faster
  rhostsize = 1000000
  
  fg = FeatureGetter(False)

  #God mode features:
  #featuredimension = 1

  #Normal features:
  featuredimension = fg.get_dimension()

  get_feature_function = fg.get_features
    
  sq = get_sqler()
  #overallnum_sets = sq.get_num_compsets()
  #num_sets = int(overallnum_sets*percentage)
  #overallnum_testsets = sq.get_num_compsets(validation = True)
  just_winning_sets = False
  testing = False # should be false to get the full data set
  #testing = True # should be false to get the full data set
  
  # sleeping so that we dont kill database
  #sec = 20*comm_rank
  #print "machine %d is sleeping for %d sec."%(comm_rank,sec)
  #time.sleep(sec)
  
  for i in range(2,comm_size+2,3):
    if comm_rank==i or comm_rank==i-1 or comm_rank==i-2:
      print "Machine %d/%d - Start loading the competitorsets for TRAIN"%(comm_rank,comm_size)
      t0 = time.time()
      num_sets = 100000 # TODO remove
      print num_sets

      # TODO: CAREFULL - num_sets shouldn't be bigger than 500000
    #  if num_sets > 500000:
    #    raise RuntimeError('num_sets should not be larger than 500000. That takes \
    #      already 2.3G mem and we dont wanna run into mem errors')
      cs_train = CompetitorSetCollection(num_sets=num_sets, mode = 'train')

      t1 = time.time()
      print "Machine %d/%d - Finished loading the competitorsets for TRAIN."%(comm_rank,comm_size)
      print "Loading competitorsets took %s."%(t1-t0)
 
    safebarrier(comm)
  
  
  # sleeping so that we dont kill database
  sec = comm_rank
  print "machine %d is sleeping for %d sec."%(comm_rank,sec)
  time.sleep(sec)
  
  # CV over lamba1, lambda2
  #lambdas = [10**-3, 10**-2, 10**-1, 10**0, 10**+1]
  #lambdas = [10**-1]

  trainerrors = np.zeros((len(lambdas),len(lambdas)))
  testerrors = np.zeros((len(lambdas),len(lambdas)))
  trainmeannrank = np.zeros((len(lambdas),len(lambdas)))
  testmeannrank = np.zeros((len(lambdas),len(lambdas)))
  
  for lw in range(len(lambdas)):
  #for lw,lambda_winner in enumerate(lambdas):
    #for lr,lambda_reject in enumerate(lambdas):
      lambda_winner, lambda_reject = lambdas[lw]
      lr = lw # we can't afford the full CV
      #lambda_reject = lambda_winner #* 10.0
        
      # Create sgd object   
      if personalization:
        sgd = SGDLearningPersonalized(featuredimension, get_feature_function, memory_for_personalized_parameters) # featdim +1 iff cheating
      else:
        #sgd = SGDLearning(featuredimension, get_feature_function) # without personalization/hashing, faster
        sgd = SGDLearningRHOSTHASH(featuredimension, get_feature_function, rhostsize=rhostsize)
        
      N = cs_train.get_nsamples()
      niter = int(N*nepoches)
      
      for outit in range(outer_iterations):
        # for each outer iteration we draw new samples iid per node
        sampleindices = []
        for _ in range(int(nepoches)+1):
          sampleindices += range(N)
        #sampleindices = range(N)
        
        random.shuffle(sampleindices)
        update_lookahead_cnt = 0
        req_ids = cs_train.get_req_ids_for_samples(sampleindices[0:LOOK_AHEAD_LENGTH])
        fg.upt_out_prod_get(req_ids)
        
#        from IPython import embed
#        embed()  
        for innerit in range(niter):
          i = outit*niter + innerit
          eta_t = 1/sqrt(alpha+i*beta)
          if not i%(niter/5):
              print "Machine %d/%d - Iterations out: %d/%d - in: %d/%d - eta %f - lambda %f"%(comm_rank, comm_size, outit+1,outer_iterations, innerit+1,niter,eta_t, lambda_winner)
          
          update_lookahead_cnt += 1
          if update_lookahead_cnt == LOOK_AHEAD_LENGTH:
            req_ids = cs_train.get_req_ids_for_samples(sampleindices[innerit:innerit+LOOK_AHEAD_LENGTH])
            fg.upt_out_prod_get(req_ids)
            update_lookahead_cnt = 0
          
          # draw random sample - UPDATE: now first get a random permutation, then do it            
          sampleindex = sampleindices[innerit]    
          competitorset = cs_train.get_sample(sampleindex)

          for l in competitorset.get_surferlist():
            assert(l[1] in req_ids)
  
          if verbose and not i%10000 and i>1:
              print "Iterations \n\tout: %d/%d \n\tin: %d/%d - eta %f - lambda %f"%(outit+1,outer_iterations, innerit+1,niter,eta_t, lambda_winner)
              print "\ttheta", min(sgd.theta), max(sgd.theta)
              print "\tr", sgd.r
              print "\tr_hosts", sgd.r_hosts.get(competitorset.get_hostID(), -999) ,min(sgd.r_hosts.values()), max(sgd.r_hosts.values()) 
              print "\ttrue", competitorset.get_winner()
              print "\tpredicted", sgd.predict(competitorset)
              print "\tranking", sgd.rank(competitorset)
          sgd.update(competitorset, eta=eta_t, lambda_winner=lambda_winner, lambda_reject=lambda_reject)

        # Now we aggregate theta(_host), r(_host)
        print "outer iteration %d/%d: node %d at safebarrier"%(outit+1, outer_iterations, comm_rank)
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
              
        # For the r_hosts we need to juggle a little bit to get it going
        # Just build the mean over all machines that actually touched a specific host
        #if comm_rank == 0:
          #embed()
        #safebarrier(comm)
        
        #r_hosts_orig = sgd.r_hosts
        #r_hosts_list = comm.allreduce([sgd.r_hosts])
        #if comm_rank == 0:
        #  print "allreduce done for r_hosts"
        
        #my_hosts = r_hosts_orig.keys()
        #host_count = {k:0 for k in my_hosts}
        #new_r_hosts = {k:0 for k in my_hosts}
        #for other_hosts in r_hosts_list:
        #  for key in other_hosts:
        #    if key in my_hosts:
        #      host_count[key] += 1
        #      new_r_hosts[key] += other_hosts[key]
        #for k in new_r_hosts:
        #  new_r_hosts[k] /= host_count[k]      
        #r_hosts = new_r_hosts
        #if comm_rank == 0:
        #  print "special computing done for r_hosts"
        
        
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
          dirname = '/tscratch/tmp/csrec/'
          if os.path.exists('/tscratch'):
            if not os.path.exists(dirname):
              os.makedirs(dirname)
          # 777 permission on directory
          os.system('chmod -R 777 '+dirname)
              
          filename = 'parameters_lwin_%f_lrej_%f_testing_%d_personalized_%d_numsets_%d_outerit_%d_nepoches_%d.pkl'%(lambda_winner, lambda_reject, testing, personalization, num_sets, outer_iterations,nepoches)
          if os.path.exists('/tscratch'):
            if personalization:
              pickle.dump( (sgd.theta, sgd.theta_hosts, sgd.r, sgd.r_hosts), open( dirname+filename, "wb" ) )
            else:
              pickle.dump( (sgd.theta, sgd.r, sgd.r_hosts), open( dirname+filename, "wb" ) )
              print "Stored params at " + dirname+filename  
                
      # Compute the errors
      safebarrier(comm)
      
      errorrate, truenonerate, prednonerate = test_predictionerror(fg, sgd, cs_train)
      meannrank = test_meannormalizedwinnerrank(fg, sgd, cs_train)
      trainerrors[lw,lr] = errorrate
      trainmeannrank[lw,lr] = meannrank
      if comm_rank == 0:
        if verbose:
          print "[TRAIN] Errorrate: %f"%(errorrate)
          print "TrueNone-Rate: %f -> error: %f"%(truenonerate, 1.0 - truenonerate)
          print "PredNone-Rate: %f"%(prednonerate)
          print "MEANNRANK: %f"%(meannrank)
      
      # need to sleep again st we don't kill database
      #print "machine %d is sleeping for %d sec."%(comm_rank,sec)
      #time.sleep(sec)
      
      for i in range(2,comm_size+2,3):
        if comm_rank==i or comm_rank==i-1 or comm_rank==i-2:
          print "Machine %d/%d - Start loading the competitorsets for VAL"%(comm_rank,comm_size)
          cs_test = CompetitorSetCollection(num_sets=num_sets, mode='val')
          
        safebarrier(comm)
      
      errorrate, truenonerate, prednonerate = test_predictionerror(fg, sgd, cs_test)
      testerrors[lw,lr] = errorrate
      meannrank = test_meannormalizedwinnerrank(fg, sgd, cs_test)
      testerrors[lw,lr] = errorrate
      testmeannrank[lw,lr] = meannrank
      if comm_rank == 0:
        if verbose:
          print "[VAL] Errorrate: %f"%(errorrate)
          print "TrueNone-Rate: %f -> error: %f"%(truenonerate, 1.0 - truenonerate)
          print "PredNone-Rate: %f"%(prednonerate)
          print "MEANNRANK: %f"%(meannrank)




  # end of CV for loops

  # show the final errors
  if comm_rank == 0:
    print "lambdas:", lambdas
    print "winner/reject"            
    print "TRAINerrormatrix"
    print trainerrors            

    print "VALerrormatrix"
    print testerrors            


    print "TRAINmeannrankMatrix"
    print trainmeannrank        

    print "TESTmeannrankMatrix"
    print testmeannrank 
    
    
    # store errorrates somewhere
    filename = 'errors_lwin_%f_lrej_%f_testing_%d_personalized_%d_numsets_%d_outerit_%d_nepoches_%d.pkl'%(lambda_winner,lambda_reject,testing,personalization,num_sets, outer_iterations,nepoches)
    
    if os.path.exists('/tscratch'):
      pickle.dump( (trainerrors, testerrors, trainmeannrank, testmeannrank), open( dirname+filename, "wb" ) )
      os.system('chmod -R 777 '+dirname)    
     
if __name__=='__main__':
  run()
