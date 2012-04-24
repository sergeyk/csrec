# -*- coding: utf-8 -*-
"""
Created on Thu Apr 19 17:34:55 2012

@author: Tim
"""

from competitor_sets.competitor_sets import CompetitorSet, CompetitorSetCollection

# get data (Tobi)
dataobject = CompetitorSetCollection()
print dataobject.get_nsamples() # N
print dataobject.get_sample(17) # yields a competitorset
# TODO: Tobi - put your stuff here


# get featuremethod (Ron)
from features.user_features import FeatureGetter

fg = FeatureGetter()
#print fg.get_features(907345, 907345, 1)
dimension = fg.get_dimension()


# create SGD object, sample different competitorsets, and do learning
from gradientdescent import SGDLearning
import random

sgd = SGDLearning(dimension, fg.get_features)

niter = 100
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
    #print "\ttheta", sgd.theta
    print "\tr", sgd.r
    print "\tr_hosts", sgd.r_hosts
    print "\ttrue", competitorset.get_winner()
    print "\tpredicted", sgd.predict(competitorset)
    
    sgd.update(competitorset, eta=0.1, regularization_lambda=0.1)
    
    
# TESTING
errors = 0
for i in range(N-8):
    #TODO: dirty hack
    if i < 8:
      i += 8
    competitorset = dataobject.get_sample(i)
    
    pred = sgd.predict(competitorset)
    true = competitorset.get_winner()
    errors += (pred!=true)
    
print "Errorrate: %f (%d/%d)"%(errors/float(N), errors, N)
    
    
    
    
    
    
    
    
    
    
    
    
    
