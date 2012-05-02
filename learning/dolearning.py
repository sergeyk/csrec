from competitor_sets.competitor_sets import CompetitorSet, CompetitorSetCollection
from math import sqrt
from time import time
from IPython import embed
import numpy as np


# get data (Tobi)
testing = True
dataobject = CompetitorSetCollection(testing=testing,validation=False)
print dataobject.get_nsamples() # N
print dataobject.get_sample(17) # yields a competitorset
# TODO: Tobi - put your stuff here

# get featuremethod (Ron)
from features.user_features import FeatureGetter

fg = FeatureGetter(testing)
#print fg.get_features(907345, 907345, 1)
dimension = fg.get_dimension()


# create SGD object, sample different competitorsets, and do learning
from gradientdescent import SGDLearning
from gradientdescent_personalization import SGDLearningPersonalized
import random


# it is better to load all competitorsets at once and then do learning fast
traindataobject = CompetitorSetCollection(testing=True,validation=False)
Ntrain = traindataobject.get_nsamples()
competitorsets_train = [traindataobject.get_sample(i) for i in xrange(Ntrain)]

testdataobject = CompetitorSetCollection(testing=True, validation=True)
Ntest = testdataobject.get_nsamples()
competitorsets_test = [testdataobject.get_sample(i) for i in xrange(Ntest)]
print "loaded all training and testing examples into memory"



def train(sgd, competitorsets_train, niter, alpha, beta, lambda_winner, lambda_reject, verbose):
    N = len(competitorsets_train)
    # TRAINING
    # do a couple update steps
    t0 = time()
    for i in range(niter):
        eta_t = 1/sqrt(alpha+i*beta)
        if not i%(niter/10):
            print "Iteration %d/%d - eta %f"%(i,niter,eta_t)

        # draw random sample  
        sampleindex = random.randint(0,N-1)    
        #competitorset = dataobject.get_sample(sampleindex)
        competitorset = competitorsets_train[sampleindex]
        
        if verbose and not i%1000 and i>1:
            print "Iteration %d/%d - eta %f"%(i,niter,eta_t)
            print "\ttheta", min(sgd.theta), max(sgd.theta)
            print "\tr", sgd.r
            print "\tr_hosts", sgd.r_hosts.get(competitorset.get_hostID(), -999) ,min(sgd.r_hosts.values()), max(sgd.r_hosts.values()) 
            print "\ttrue", competitorset.get_winner()
            print "\tpredicted", sgd.predict(competitorset)
            
        sgd.update(competitorset, eta=eta_t, lambda_winner=lambda_winner, lambda_reject=lambda_reject)    

    t1 = time()
    print "Time for learning:", t1-t0
    print "avg Time per iteration:", (t1-t0)/float(niter)   
 
 
def test(sgd, data): 
    errors = 0
    truenones = 0
    prednones = 0
    N = len(data)
    for i in range(N):
        competitorset = data[i]
        pred = sgd.predict(competitorset)
        true = competitorset.get_winner()
        #if true:
        #  print 'prediction', pred
        #  print 'true val', true
            
        errors += (pred!=true)
        truenones += (true==None)
        prednones += (pred==None)
        
    errorrate = errors/float(N)  
    truenonerate = truenones/float(N)  
    prednonerate = prednones/float(N) 
    return errorrate, truenonerate, prednonerate
 

# CV over lamba1, lambda2
lambdas = [10**-4, 10**-3, 10**-2, 10**-1, 10**0, 10**+1, 10**+2]
#lambdas = [10**-3]
trainerrors = np.zeros((len(lambdas),len(lambdas)))
testerrors = np.zeros((len(lambdas),len(lambdas)))

featuredimension = fg.get_dimension()
get_feature_function = fg.get_features

memory_for_personalized_parameters = 10.0 # memory in MB if using personalized SGD learning

# learning parameters
niter = int(10.0 * Ntrain)
alpha = 100.0
beta = 0.01
#lambda_winner = 0.01#0.01
#lambda_reject = 0.1
verbose = False

for i,lambda_winner in enumerate(lambdas):
    for j,lambda_reject in enumerate(lambdas):
        #sgd = SGDLearning(featuredimension, get_feature_function)
        #sgd = SGDLearning(1, get_feature_function) # CHEAT TODO REMOVE
        #sgd = SGDLearning(featuredimension+1, get_feature_function) # CHEAT TODO REMOVE
        sgd = SGDLearningPersonalized(featuredimension, get_feature_function, memory_for_personalized_parameters) # featdim +1 iff cheating
  
        # TRAINING
        train(sgd, competitorsets_train, niter, alpha, beta, lambda_winner, lambda_reject, verbose)

        # TESTING - TRAINSET
        errorrate, truenonerate, prednonerate = test(sgd, competitorsets_train)
        trainerrors[i,j] = errorrate
        if verbose:
            print "[TRAIN] Errorrate: %f"%(errorrate)
            print "TrueNone-Rate: %f -> error: %f"%(truenonerate, 1.0 - truenonerate)
            print "PredNone-Rate: %f"%(prednonerate)
  
        # TESTING - TESTSET
        errorrate, truenonerate, prednonerate = test(sgd, competitorsets_test)
        testerrors[i,j] = errorrate
        if verbose:
            print "[TEST] Errorrate: %f"%(errorrate)
            print "TrueNone-Rate: %f -> error: %f"%(truenonerate, 1.0 - truenonerate)
            print "PredNone-Rate: %f"%(prednonerate)
            

print "lambdas:", lambdas
print "winner/reject"            
print "TRAINerrormatrix"
print trainerrors            

print "TESTerrormatrix"
print testerrors            


embed()       
    
    
    
