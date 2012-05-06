# -*- coding: utf-8 -*-
"""
Realization of the update equations in derivation.pdf
Here, for the case with personalized host parameters theta_h
We assume the following format:
    - update(old_params, competitorset) -> new_params
    - get_feature(surferID, hostID, couchrequestID) -> 1D numpy array
    - competitorset structure: dict with keys hostID, list_surfers [(surferID, requestID), ...], winner (surferID or None if all rejected)

TODO:
    - sparse dot product -> sparse features and only compute hash for nonzeroparts
      -> seems simpler than to compute features here on the fly
    - rademacher hash (seems to work but be careful :-))

@author: Tim
"""

import numpy as np
from IPython import embed


# Set this to true if you would like to use "perfect" features. 
# Also: turn on God mode in run_mpi
SANITY_CHECK = False

def inthash(x,y,N): # take this one
    a = (x * 0x1f1f1f1f) ^ y
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

## rademacher (binary) hash: TODO: is there a better/easier way to do it?
#def rademacher(x,y):
#    a = ((y & 0xffff) << 16) | (x & 0xffff)
#    a = (a ^ 61) ^ (a >> 16)
#    a = a + (a << 3)
#    a = a ^ (a >> 4)
#    a = a * 0x27d4eb2d
#    a = a ^ (a >> 15)
#    # make it binary by looking at a bit in the middle
#    a = a>>7 & 1
#    a = 2*a - 1
#    return a      
    
def argsort(seq):
    # http://stackoverflow.com/questions/3071415/efficient-method-to-calculate-the-rank-vector-of-a-list-in-python
    return sorted(range(len(seq)), key=seq.__getitem__, reverse=True)


class SGDLearningPersonalized:

    def __init__(self, featuredimension, get_feature_function, memory_for_personalized_parameters, theta=None, r=None, r_hosts=None, theta_hosts=None):
        self.featuredimension = int(featuredimension)
        self.theta = theta if theta!=None else 0.2*(np.random.rand(featuredimension+1) - 0.5) # +1 to learn bias term
        self.r = r if r else 0.0
        #r_hosts = np.zeros(nhosts) # do I need dictionary here: hostID -> param?
        self.r_hosts = r_hosts if r_hosts else {}
        self.get_feature = get_feature_function
        
        if theta_hosts!=None:
            self.theta_hosts = theta_hosts
            self.nelements = len(self.theta_hosts)
        else:
            # build large array that the personalized host parameters are hashed into
            self.nelements = int(memory_for_personalized_parameters * 1000000 / 8.0) # assuming 64bit floats, and memory in MB
			#TODO: does it make sense to initialize this randomly?
            self.theta_hosts = 0.2*(np.random.rand(self.nelements) - 0.5) #np.zeros(self.nelements)
    
    def get_score(self, feature, theta_h):
        return np.exp(np.dot(self.theta + theta_h,feature))
        
    def get_rejectscore(self, hostID):
        # if we don't have a r_host yet create one with param zero
        if not self.r_hosts.has_key(hostID):
            self.r_hosts[hostID] = 0.0
            
        return np.exp(self.r + self.r_hosts[hostID])

    def get_hostparameters(self, hostID):
        # TODO: I could compute indizes for nonzero elements of the feature only
        indizes = [inthash(hostID,i,self.nelements) for i in range(self.featuredimension+1)] # +1 because of bias term
        indizes, rademacherflips = zip(*indizes)
        indizes = np.array(indizes)
        rademacherflips = np.array(rademacherflips) # tuple -> array
        theta_h = self.theta_hosts[indizes]
        theta_h = theta_h * rademacherflips
        return theta_h

    def predict(self, competitorset):
        cand, scores = self.rank(competitorset)
        return cand[0]
   
    def rank(self, competitorset):
        # used for inference later and to evaluate error on testset
        hostID = competitorset.get_hostID()        
        
        # if we don't have a r_host yet create one with param zero
        if not self.r_hosts.has_key(hostID):
            self.r_hosts[competitorset.get_hostID()] = 0.0
        
        # before without bias
        #features = [self.get_feature(surferID,hostID,requestID) for (surferID, requestID) in competitorset.get_surferlist()] 

        # with appended 1 feature for bias term using ron's feature getter
        features = [np.append(self.get_feature(surferID,hostID,requestID),np.ones(1)) for (surferID, requestID) in competitorset.get_surferlist()] 

        # CHEAT TODO REMOVE
        #features = [np.hstack((self.get_feature(surferID,hostID,requestID),np.ones(1)*(surferID==competitorset.get_winner()), np.ones(1))) for (surferID, requestID) in competitorset.get_surferlist()]

        # w Bias CHEAT TODO REMOVE
        if SANITY_CHECK:
            features = [np.append(2*(np.ones(1)*(surferID==competitorset.get_winner()))-1, np.ones(1)) for (surferID, requestID) in competitorset.get_surferlist()]
        
        # get personalized hostparameters
        #theta_h = self.get_hostparameters(hostID)
        indizes = [inthash(hostID,i,self.nelements) for i in range(self.featuredimension+1)] # +1 because of bias term
        indizes, rademacherflips = zip(*indizes)
        indizes = np.array(indizes)
        rademacherflips = np.array(rademacherflips) # tuple -> array
        theta_h = self.theta_hosts[indizes]
        theta_h = theta_h * rademacherflips
        #print "PERS PARAMS", hostID, theta_h # TODO remove
        
        scores = [self.get_score(f, theta_h) for f in features]
        rejectscore = self.get_rejectscore(hostID)
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
        # if we don't have a r_host yet create one with param zero
        if not self.r_hosts.has_key(hostID):
            self.r_hosts[hostID] = 0.0        
        
        # get features, scores, and probabilities
        #features = [self.get_feature(surferID,hostID,requestID) for (surferID, requestID) in competitorset.get_surferlist()] # before without bias
        features = [np.append(self.get_feature(surferID,hostID,requestID),np.ones(1)) for (surferID, requestID) in competitorset.get_surferlist()] # with appended 1 feature for bias term
        #features = [np.hstack((self.get_feature(surferID,hostID,requestID),np.ones(1)*(surferID==competitorset.get_winner()), np.ones(1))) for (surferID, requestID) in competitorset.get_surferlist()] # CHEAT TODO REMOVE
        if SANITY_CHECK:
            features = [np.append(2*(np.ones(1)*(surferID==competitorset.get_winner()))-1, np.ones(1)) for (surferID, requestID) in competitorset.get_surferlist()] # w Bias CHEAT TODO REMOVE

        # get personalized hostparameters
        #theta_h = self.get_hostparameters(hostID) 
        indizes = [inthash(hostID,i,self.nelements) for i in range(self.featuredimension+1)] # +1 because of bias term
        indizes, rademacherflips = zip(*indizes)
        indizes = np.array(indizes)
        rademacherflips = np.array(rademacherflips) # tuple -> array
        theta_h = self.theta_hosts[indizes]
        theta_h = theta_h * rademacherflips
        
        scores = [self.get_score(f, theta_h) for f in features]
        rejectscore = self.get_rejectscore(hostID)
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
            self.r_hosts[hostID] =  (1 - eta * lambda_reject) * self.r_hosts[hostID] - eta * (rejectprobability - 1) 

            # update of personalized host parameters
            self.theta_hosts[indizes] = rademacherflips * ((1 - eta * lambda_winner) * theta_h - eta * np.sum(temp, axis=0)) # TODO make sure that the flipping makes sense!
        else:
            # there was a winner
            winneridx = zip(*competitorset.get_surferlist())[0].index(competitorset.get_winner())
            
            temp = [p*f for (p,f) in zip(probabilities,features)]
            self.theta = (1 - eta * lambda_winner) * self.theta - eta * (np.sum(temp, axis=0) - features[winneridx])
            #self.r = self.r - eta * rejectprobability
            self.r = (1 - eta * lambda_reject) * self.r - eta * rejectprobability
            self.r_hosts[hostID] =  (1 - eta * lambda_reject) * self.r_hosts[hostID] - eta * rejectprobability 

            # update of personalized host parameters
            self.theta_hosts[indizes] = rademacherflips * ((1 - eta * lambda_winner) * theta_h - eta * (np.sum(temp, axis=0) - features[winneridx]))
    


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
        
        if hostID==0: # to test out whether the host params pick up the signal
            return -feat
        else:
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
            
    class CompetitorSet3: # reje!=Nonect Host
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
    memsize = 1 #MB
    #sgd = SGDLearningPersonalized(featuredimension, get_feature_function, memsize)
    theta = np.arange(3)
    r = 17
    r_hosts = {}
    theta_hosts = np.random.rand(20) - 0.5
    sgd = SGDLearningPersonalized(featuredimension, get_feature_function, memsize) # the +1 is if were cheating, inside the object definition is another +1 which is for the bias term
    #sgd = SGDLearningPersonalized(featuredimension+1, get_feature_function, memsize, theta=theta, r=r, r_hosts=r_hosts, theta_hosts=theta_hosts)    
    
    niter = 100
    
    # do a couple update steps
    for i in range(niter):
        cs = competitorsets[i%len(competitorsets)] # iterate throught different competitorsets  
        
        print "iteration", i
        print "\ttheta", sgd.theta
        theta_h = sgd.get_hostparameters(cs.get_hostID())
        print "\ttheta_host", theta_h
        print "\ttheta_total", theta_h + sgd.theta
        winnerfeat = get_feature(cs.get_winner(), cs.get_hostID(), cs.get_winner())
        print "\twinnerfeat", winnerfeat
        print "\tr", sgd.r
        print "\tr_hosts", sgd.r_hosts
        print "\ttrue", cs.get_winner()
        print "\tpredicted", sgd.predict(cs)
        print "\tranking", sgd.rank(cs)
        
        sgd.update(cs, eta=0.1, lambda_winner=0.1, lambda_reject=0.1)
        
    
