# -*- coding: utf-8 -*-
"""
Realization of the update equations in derivation.pdf
We assume the following format:
    - update(old_params, competitorset) -> new_params
    - get_feature(surferID, hostID, couchrequestID) -> 1D numpy array
    - competitorset structure: dict with keys hostID, list_surfers [(surferID, requestID), ...], winner (surferID or None if all rejected)

TODO:
    - allow to initialize learning with given parameters (e.g. "in the middle of learning")

@author: Tim
"""

import numpy as np

def hosthash(a,N): # take this one
    a = (a ^ 61) ^ (a >> 16)
    a = a + (a << 3)
    a = a ^ (a >> 4)
    a = a * 0x27d4eb2d
    a = a ^ (a >> 15)
    # use last bit as rademacher hash
    # and rest for location
    r = 2*float(a&1)-1
    a = (a>>1)%N
    return a,r 

def argsort(seq):
    # http://stackoverflow.com/questions/3071415/efficient-method-to-calculate-the-rank-vector-of-a-list-in-python
    return sorted(range(len(seq)), key=seq.__getitem__, reverse=True)

class SGDLearningRHOSTHASH:

    def __init__(self, featuredimension, get_feature_function, rhostsize=10000, theta=None, r=None, r_hosts=None):
        #self.theta = theta if theta else np.zeros(featuredimension) 
        self.theta = theta if theta!=None else 0.2*(np.random.rand(featuredimension+1) - 0.5) # +1 to learn bias term
        self.r = r if r else 0.0
        #r_hosts = np.zeros(nhosts) # do I need dictionary here: hostID -> param?
        self.rhostsize = rhostsize
        self.r_hosts = r_hosts if r_hosts else np.zeros(rhostsize)
        self.get_feature = get_feature_function
    
    def get_score(self, feature):
        return np.exp(np.dot(self.theta,feature))
        
    def get_rejectscore(self, hostID):
        hidx, rademacher = hosthash(hostID,self.rhostsize)
        return np.exp(self.r + rademacher*self.r_hosts[hidx])
 
    def predict(self, competitorset, testingphase=False):
        cand, scores = self.rank(competitorset, testingphase=testingphase)
        return cand[0]
    
    def rank(self, competitorset, testingphase=False):
        # used for inference later and to evaluate error on testset
        hostID = competitorset.get_hostID()        
        
        #features = [self.get_feature(surferID,hostID,requestID) for (surferID, requestID) in competitorset.get_surferlist()] # before without bias
        features = [np.append(self.get_feature(surferID,hostID,requestID),np.ones(1)) for (surferID, requestID) in competitorset.get_surferlist()] # with appended 1 feature for bias term
        #features = [np.hstack((self.get_feature(surferID,hostID,requestID),np.ones(1)*(surferID==competitorset.get_winner()), np.ones(1))) for (surferID, requestID) in competitorset.get_surferlist()] # CHEAT TODO REMOVE
        #features = [np.append(2*(np.ones(1)*(surferID==competitorset.get_winner()))-1, np.ones(1)) for (surferID, requestID) in competitorset.get_surferlist()] # w Bias CHEAT TODO REMOVE
        scores = [self.get_score(f) for f in features]
        hidx, rademacher = hosthash(hostID,self.rhostsize)
        rejectscore = np.exp(self.r + rademacher*self.r_hosts[hidx])
        
        scores.append(rejectscore)
        candidates = list(zip(*competitorset.get_surferlist())[0])
        candidates.append(None)
        idx = argsort(scores)
        sortedscores = [scores[i] for i in idx]
        sortedcandidates = [candidates[i] for i in idx]
        #print "SORTEDSCORES", sortedscores
        #print "SORTEDCANDIDATES", sortedcandidates
        return sortedcandidates, sortedscores
        
    
    def update(self, competitorset, eta=0.01, lambda_winner=0.1, lambda_reject=1.0):
        hostID = competitorset.get_hostID()       
        
        # get features, scores, and probabilities
        #features = [self.get_feature(surferID,hostID,requestID) for (surferID, requestID) in competitorset.get_surferlist()] # before without bias
        features = [np.append(self.get_feature(surferID,hostID,requestID),np.ones(1)) for (surferID, requestID) in competitorset.get_surferlist()] # with appended 1 feature for bias term
        #features = [np.hstack((self.get_feature(surferID,hostID,requestID),np.ones(1)*(surferID==competitorset.get_winner()), np.ones(1))) for (surferID, requestID) in competitorset.get_surferlist()] # CHEAT TODO REMOVE
        #features = [np.append(2*(np.ones(1)*(surferID==competitorset.get_winner()))-1, np.ones(1)) for (surferID, requestID) in competitorset.get_surferlist()] # w Bias CHEAT TODO REMOVE
        scores = [self.get_score(f) for f in features]
        hidx, rademacher = hosthash(hostID,self.rhostsize)
        rejectscore = np.exp(self.r + rademacher*self.r_hosts[hidx])
        normalizer = float(np.sum(scores) + rejectscore)
        probabilities = [s/normalizer for s in scores]
        rejectprobability = rejectscore / normalizer

        
        # update params based on ground truth
        if competitorset.get_winner()==None:
            # gt -> all got rejected
            temp = [p*f for (p,f) in zip(probabilities,features)]
            self.theta =  (1 - eta * lambda_winner) * self.theta - eta * np.sum(temp, axis=0)
            #self.r = self.r - eta * (rejectprobability - 1)
            self.r = (1 - eta * lambda_reject) * self.r - eta * (rejectprobability - 1)
            self.r_hosts[hidx] =  rademacher*((1 - eta * lambda_reject) * rademacher*self.r_hosts[hidx] - eta * (rejectprobability - 1))
        else:
            # there was a winner
            winneridx = zip(*competitorset.get_surferlist())[0].index(competitorset.get_winner())
            
            temp = [p*f for (p,f) in zip(probabilities,features)]
            self.theta = (1 - eta * lambda_winner) * self.theta - eta * (np.sum(temp, axis=0) - features[winneridx])
            #self.r = self.r - eta * rejectprobability
            self.r = (1 - eta * lambda_reject) * self.r - eta * rejectprobability
            self.r_hosts[hidx] =  rademacher*((1 - eta * lambda_reject) * rademacher*self.r_hosts[hidx] - eta * rejectprobability)
            

if __name__=='__main__':
    print 'Preliminary testing of gradient descent update equations:'
    
    # build fake features
    def get_feature(surferID, hostID, couchrequestID):
        feat = np.zeros(3)
        if surferID==cs.get_winner():
            feat[0] = 1 # later try 2,1 
        else: 
            feat[0] = -1
        feat[1] = 2
        
        #if hostID==0: # to test out whether the host params pick up the signal
        #    return -feat
        #else:
        #    return feat
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
            
    class CompetitorSet2: # different winner with different features
        def get_hostID(self):
            return 1
            
        def get_surferlist(self):
            return [(1,1), (2,2), (3,3)]
        
        def get_winner(self):
            return 2 
            
    class CompetitorSet3: # reject Host
        def get_hostID(self):
            return 2
            
        def get_surferlist(self):
            return [(1,1), (2,2), (3,3)]
        
        def get_winner(self):
            return None
    
    competitorset = CompetitorSet()
    competitorset2 = CompetitorSet2()
    competitorset3 = CompetitorSet3()
    competitorsets = [competitorset, competitorset, competitorset, competitorset2, competitorset3]
    featuredimension = 3
    get_feature_function = get_feature # here Ron's function should go
    sgd = SGDLearningRHOSTHASH(featuredimension, get_feature_function, rhostsize=12)
    
    niter = 1000
    
    # do a couple update steps
    for i in range(niter):
        cs = competitorsets[i%len(competitorsets)] # iterate throught different competitorsets  
        
        print "iteration", i
        print "\ttheta", sgd.theta
        winnerfeat = get_feature(cs.get_winner(), cs.get_hostID(), cs.get_winner())
        print "\twinnerfeat", winnerfeat
        print "\tr", sgd.r
        print "\tr_hosts", sgd.r_hosts
        hidx, rademacher = hosthash(cs.get_hostID(),sgd.rhostsize)
        print "\thost", cs.get_hostID(), "rademacher",rademacher, "r_h", rademacher*sgd.r_hosts[hidx], "r+r_h", sgd.r+rademacher*sgd.r_hosts[hidx]
        print "\ttrue", cs.get_winner()
        print "\tpredicted", sgd.predict(cs)
        print "\tranking", sgd.rank(cs)
        
        sgd.update(cs, eta=0.1, lambda_winner=0.1, lambda_reject=0.1)
        
   
