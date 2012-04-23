# -*- coding: utf-8 -*-
"""
Created on Thu Apr 19 17:34:55 2012

@author: Tim
"""

# get data (Tobi)
dataobject = None
print dataobject.get_nsamples() # N
print dataobject.get_sample(17) # yields a competitorset
# TODO: Tobi - put your stuff here


# get featuremethod (Ron)
from features.user_features import FeatureGetter

fg = FeatureGetter()
print fg.get_features(907345, 907345, 1)
print fg.get_dimension()


# create SGD object, sample different competitorsets, and do learning
from gradientdescent import SGDLearning
import random

sgd = SGDLearning()

niter = 10
N = dataobject.get_nsamples()
featuredimension = fg.get_dimension()
get_feature_function = fg.get_features
sgd = SGDLearning(featuredimension, get_feature_function)

# TRAINING
# do a couple update steps
for i in range(niter): 
    # draw random sample  
    sampleindex = random.randint(0,N-1)    
    competitorset = dataobject.get_sample(sampleindex)  
    
    print "iteration", i
    print "\ttheta", sgd.theta
    print "\tr", sgd.r
    print "\tr_hosts", sgd.r_hosts
    print "\ttrue", competitorset.get_winner()
    print "\tpredicted", sgd.predict(competitorset)
    
    sgd.update(competitorset, eta=0.1, regularization_lambda=0.1)
    
    
# TESTING
errors = 0
for i in range(N):
    competitorset = dataobject.get_sample(i) # TODO: Tobi, here we need a way to access the test set
    pred = sgd.predict(competitorset)
    true = competitorset.get_winner()
    errors += (pred!=true)
    
print "Errorrate: %f (%d/%d)"%(errors/float(N), errors, N)
    
    
    
    
    
    
    
    
    
    
    
    
    