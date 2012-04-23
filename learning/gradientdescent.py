# -*- coding: utf-8 -*-
"""
Realization of the update equations in derivation.pdf
We assume the following format:
    - update(old_params, competitorset) -> new_params
    - get_feature(surferID, hostID, couchrequestID) -> 1D numpy array
    - competitorset structure: dict with keys hostID, list_surfers [(surferID, requestID), ...], winner (surferID or None if all rejected)

TODO:
    - names for getterfunctions for tobi
    - toplevel file that reads data from tobi and does learning
    - testcode 

@author: Tim
"""

import numpy as np


class SGDLearning:

    def __init__(self, featuredimension, get_feature_function):
        self.theta = np.zeros(featuredimension)
        self.r = 0
        #r_hosts = np.zeros(nhosts) # do I need dictionary here: hostID -> param?
        self.r_hosts = {}
        self.get_feature = get_feature_function
    
    def get_score(self, feature):
        return np.exp(np.dot(self.theta,feature))
        
    def get_rejectscore(self, hostID):
        # if we don't have a r_host yet create one with param zero
        if not self.r_hosts.has_key(hostID):
            self.r_hosts[hostID] = 0.0
            
        return np.exp(self.r + self.r_hosts[hostID])
    
    def predict(self, competitorset):
        # used for inference later and to evaluate error on testset
        
        # if we don't have a r_host yet create one with param zero
        if not self.r_hosts.has_key(competitorset.get_hostID()):
            self.r_hosts[competitorset.get_hostID()] = 0.0
        
        features = [self.get_feature(surferID,competitorset.get_hostID(),requestID) for (surferID, requestID) in competitorset.get_surferlist()]
        scores = [self.get_score(f) for f in features]
        rejectscore = self.get_rejectscore(competitorset.get_hostID())
        
        maxsurfer = np.argmax(scores)
        #print "rejectscore", rejectscore
        #print "maxsurferscore", scores[maxsurfer]
        #print ""
        if rejectscore>scores[maxsurfer]:
            return None
        else: # return surferID of winner
            return competitorset.get_surferlist()[maxsurfer][0]
        
    
    def update(self, competitorset, eta=0.01, regularization_lambda=1):
        # if we don't have a r_host yet create one with param zero
        if not self.r_hosts.has_key(competitorset.get_hostID()):
            self.r_hosts[competitorset.get_hostID()] = 0.0        
        
        # get features, scores, and probabilities
        features = [self.get_feature(surferID,competitorset.get_hostID(),requestID) for (surferID, requestID) in competitorset.get_surferlist()]
        scores = [self.get_score(f) for f in features]
        rejectscore = self.get_rejectscore(competitorset.get_hostID())
        normalizer = float(np.sum(scores) + rejectscore)
        probabilities = [s/normalizer for s in scores]
        rejectprobability = rejectscore / normalizer
        
        # update params based on ground truth
        if competitorset.get_winner()==None:
            # gt -> all got rejected
            temp = [p*f for (p,f) in zip(probabilities,features)]
            self.theta = self.theta - eta * np.sum(temp, axis=0)
            self.r = self.r - eta * (rejectprobability - 1)
            self.r_hosts[competitorset.get_hostID()] = self.r_hosts[competitorset.get_hostID()] - eta * (rejectprobability - 1) 
        else:
            # there was a winner
            winneridx = zip(*competitorset.get_surferlist())[0].index(competitorset.get_winner())
            
            temp = [p*f for (p,f) in zip(probabilities,features)]
            self.theta = self.theta - eta * (np.sum(temp, axis=0) - features[winneridx])
            self.r = self.r - eta * rejectprobability
            self.r_hosts[competitorset.get_hostID()] = self.r_hosts[competitorset.get_hostID()] - eta * rejectprobability 
        
        
        # regularization of theta, r_hosts
        if regularization_lambda>0:
            self.theta = self.theta - eta * regularization_lambda * self.theta
            self.r_hosts[competitorset.get_hostID()] = self.r_hosts[competitorset.get_hostID()] - eta * regularization_lambda * self.r_hosts[competitorset.get_hostID()] 

    


if __name__=='__main__':
    print 'Preliminary testing of gradient descent update equations:'
    
    # build fake features
    def get_feature(surferID, hostID, couchrequestID):
        feat = np.zeros(3)
        if surferID==competitorset.get_winner():
            feat[0] = 1 # later try 2,1 
        else: 
            feat[0] = -1
        feat[1] = 2
        return feat
    
#    competitorset = {
#        'hostID': 0,
#        'list_surfers': [(1,1), (2,2), (3,3)],
#        'winner': 3, # later try None
#    }
    #print competitorset
    class CompetitorSet:
        def get_hostID(self):
            return 0
            
        def get_surferlist(self):
            return [(1,1), (2,2), (3,3)]
        
        def get_winner(self):
            return 3
    
    competitorset = CompetitorSet()    
    
    featuredimension = 3
    get_feature_function = get_feature # here Ron's function should go
    sgd = SGDLearning(featuredimension, get_feature_function)
    
    # do a couple update steps
    for i in range(100):
                
        print "iteration", i
        print "\ttheta", sgd.theta
        print "\tr", sgd.r
        print "\tr_hosts", sgd.r_hosts
        print "\ttrue", competitorset.get_winner()
        print "\tpredicted", sgd.predict(competitorset)
        
        sgd.update(competitorset, eta=0.1, regularization_lambda=0.1)
        
    