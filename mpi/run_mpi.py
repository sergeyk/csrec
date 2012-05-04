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
from competitor_sets.competitor_sets import CompetitorSetCollection
from competitor_sets.Sqler import Sqler
from features.user_features import FeatureGetter
from math import sqrt
from IPython import embed
import random
import os
import os.path
import numpy as np
from learning.dolearning import test
from mpi.mpi_imports import *
try:
    import cPickle as pickle
except:
    import pickle



def run():
  if os.path.exists('/home/tobibaum/'):
    testing = True
  else:
    testing = False

  testing = True
  memory_for_personalized_parameters = 50.0 # memory in MB if using personalized SGD learning  
  percentage = 0.2 # Dependent on machines in future min:10%, 2nodes->80%
  outer_iterations = 1 #10
  nepoches = 0.02 #10
  alpha = 100.0
  beta = 0.01
  lambda_winner = 0.01
  lambda_reject = 0.01
  verbose = True
  
  fg = FeatureGetter(testing)
  featuredimension = fg.get_dimension()
  get_feature_function = fg.get_features  
  
  sq = Sqler()
  overallnum_sets = sq.get_num_compsets()
  num_sets = int(overallnum_sets*percentage)
  
  
  # CV over lamba1, lambda2
  lambdas = [10**-4, 10**-3, 10**-2, 10**-1, 10**0, 10**+1, 10**+2]
  #lambdas = [10**-3]
  trainerrors = np.zeros((len(lambdas),len(lambdas)))
  testerrors = np.zeros((len(lambdas),len(lambdas)))
  
  
  for lw,lambda_winner in enumerate(lambdas):
    for lr,lambda_reject in enumerate(lambdas):
      
      # Create sgd object   
      sgd = SGDLearningPersonalized(featuredimension, get_feature_function, memory_for_personalized_parameters) # featdim +1 iff cheating
      dataobject = CompetitorSetCollection(num_sets=num_sets, testing=testing,validation=False)
      N = dataobject.get_nsamples()
      niter = int(N*nepoches)
      
      for outit in range(outer_iterations):
        # for each outer iteration we draw new samples iid per node  
        for innerit in range(niter):
          i = outit*niter + innerit
          eta_t = 1/sqrt(alpha+i*beta)
          if not i%(niter/10):
              print "Iterations \n  out: %d/%d \n  in: %d/%d - eta %f"%(outit+1,outer_iterations, innerit+1,niter,eta_t)

          # draw random sample  
          sampleindex = random.randint(0,N-1)    
          competitorset = dataobject.get_sample(sampleindex)
          
          if verbose and not i%1000 and i>1:
              print "Iterations \n\tout: %d/%d \n\tin: %d/%d - eta %f"%(outit+1,outer_iterations, innerit+1,niter,eta_t)
              print "\ttheta", min(sgd.theta), max(sgd.theta)
              print "\tr", sgd.r
              print "\tr_hosts", sgd.r_hosts.get(competitorset.get_hostID(), -999) ,min(sgd.r_hosts.values()), max(sgd.r_hosts.values()) 
              print "\ttrue", competitorset.get_winner()
              print "\tpredicted", sgd.predict(competitorset)
              
          sgd.update(competitorset, eta=eta_t, lambda_winner=lambda_winner, lambda_reject=lambda_reject)
        
        # Now we aggregate theta(_host), r(_host)
        print "outer iteration %d/%d: node %d at safebarrier"%(outit+1, outer_iterations, comm_rank)
        safebarrier(comm)
        
        theta = comm.allreduce(sgd.theta)/float(comm_size)
        theta_hosts = comm.allreduce(sgd.theta_hosts)/float(comm_size)
        r = comm.allreduce(sgd.r)/float(comm_size)
        
        # For the r_hosts we need to juggle a little bit to get it going
        # Just build the mean over all machines that actually touched a specific host
        #if comm_rank == 0:
          #embed()
        #safebarrier(comm)
        r_hosts_orig = sgd.r_hosts
        r_hosts_list = comm.allreduce([sgd.r_hosts])
        
        my_hosts = r_hosts_orig.keys()
        host_count = {k:0 for k in my_hosts}
        new_r_hosts = {k:0 for k in my_hosts}
        for other_hosts in r_hosts_list:
          for key in other_hosts:
            if key in my_hosts:
              host_count[key] += 1
              new_r_hosts[key] += other_hosts[key]
        for k in new_r_hosts:
          new_r_hosts[k] /= host_count[k]      
        r_hosts = new_r_hosts
        
        print 'spreading mean of parameters done!'
        sgd.theta = theta
        sgd.theta_hosts = theta_hosts
        sgd.r = r
        sgd.r_hosts = r_hosts
        
      print 'done with training' 
      
      
      # Compute the errors
      if comm_rank == 0:
        cs_train = CompetitorSetCollection(num_sets=overallnum_sets, testing=testing, validation=False)
        
        errorrate, truenonerate, prednonerate = test(sgd, cs_train)
        trainerrors[lw,lr] = errorrate
        if verbose:
          print "[TRAIN] Errorrate: %f"%(errorrate)
          print "TrueNone-Rate: %f -> error: %f"%(truenonerate, 1.0 - truenonerate)
          print "PredNone-Rate: %f"%(prednonerate)
        
        overallnum_testsets = sq.get_num_compsets(validation = True)
        cs_test = CompetitorSetCollection(num_sets=overallnum_testsets, testing=testing, validation=True)
              
        errorrate, truenonerate, prednonerate = test(sgd, cs_test)
        testerrors[lw,lr] = errorrate
        if verbose:
          print "[TEST] Errorrate: %f"%(errorrate)
          print "TrueNone-Rate: %f -> error: %f"%(truenonerate, 1.0 - truenonerate)
          print "PredNone-Rate: %f"%(prednonerate)


      # Store the parameters to /tscratch/tmp/tobibaum
      if comm_rank == 0:
          dirname = '/tscratch/tmp/csrec/'
          if not os.path.exists(dirname):
            os.makedirs(dirname)
          filename = 'parameters_lwin_%f_lrej_%f_testing_%d.pkl'%(lambda_winner, lambda_reject, testing)
          pickle.dump( (sgd.theta, sgd.theta_hosts, sgd.r, sgd.r_hosts), open( dirname+filename, "wb" ) )

  # end of CV for loops

  # show the final errors
  if comm_rank == 0:
    print "lambdas:", lambdas
    print "winner/reject"            
    print "TRAINerrormatrix"
    print trainerrors            

    print "TESTerrormatrix"
    print testerrors            

    # store errorrates somewhere
    filename = 'errors_testing_%d.pkl'%(testing)
    pickle.dump( (trainerrors, testerrors), open( dirname+filename, "wb" ) )
     
     
     
     
     
if __name__=='__main__':
  run()
