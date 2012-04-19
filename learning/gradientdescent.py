# -*- coding: utf-8 -*-
"""
Realization of the update equations in derivation.pdf
We assume the following format:
    - update(old_params, competitorset) -> new_params
    - get_feature(surferID, hostID, couchrequestID) -> 1D numpy array
    - competitorset structure: dict with keys hostID, list_surfers [(surferID, requestID), ...], winner (surferID or None if all rejected)

TODO:
    - code structure -> object-oriented?
    - r_hosts

@author: Tim
"""

import numpy as np

def get_score(theta, feature):
    return np.exp(np.dot(theta,feature))
    
def get_rejectscore(r, r_hosts):
    return np.exp(r+r_hosts)

def predict(theta, r, r_hosts, competitorset):
    # used for inference later and to evaluate error on testset
    features = [get_feature(surferID,competitorset['hostID'],requestID) for (surferID, requestID) in competitorset['list_surfers']]
    scores = [get_score(theta, f) for f in features]
    rejectscore = get_rejectscore(r, r_hosts[competitorset['hostID']]) # maybe change rhosts to be dict
    
    maxsurfer = np.argmax(scores)
    #print "rejectscore", rejectscore
    #print "maxsurferscore", scores[maxsurfer]
    #print ""
    if rejectscore>scores[maxsurfer]:
        return None
    else: # return surferID of winner
        return competitorset['list_surfers'][maxsurfer][0]
    

def update(theta, r, r_hosts, competitorset, eta=0.01, regularization_lambda=1):
    # get features, scores, and probabilities
    features = [get_feature(surferID,competitorset['hostID'],requestID) for (surferID, requestID) in competitorset['list_surfers']]
    scores = [get_score(theta, f) for f in features]
    rejectscore = get_rejectscore(r, r_hosts[competitorset['hostID']]) # maybe change rhosts to be dict
    normalizer = float(np.sum(scores) + rejectscore)
    probabilities = [s/normalizer for s in scores]
    rejectprobability = rejectscore / normalizer
    
    # update params based on ground truth
    if competitorset['winner']==None:
        # gt -> all got rejected
        temp = [p*f for (p,f) in zip(probabilities,features)]
        theta = theta - eta * np.sum(temp, axis=0)
        r = r - eta * (rejectprobability - 1)
        r_hosts[competitorset['hostID']] = r_hosts[competitorset['hostID']] - eta * (rejectprobability - 1) 
    else:
        # there was a winner
        winneridx = zip(*competitorset['list_surfers'])[0].index(competitorset['winner'])
        
        temp = [p*f for (p,f) in zip(probabilities,features)]
        theta = theta - eta * (np.sum(temp, axis=0) - features[winneridx])
        r = r - eta * rejectprobability
        r_hosts[competitorset['hostID']] = r_hosts[competitorset['hostID']] - eta * rejectprobability 
    
    
    # regularization of theta, r_hosts
    if regularization_lambda>0:
        theta = theta - eta * regularization_lambda * theta
        r_hosts[competitorset['hostID']] = r_hosts[competitorset['hostID']] - eta * regularization_lambda *r_hosts[competitorset['hostID']] 
        
    return theta, r, r_hosts



if __name__=='__main__':
    print 'Preliminary testing of gradient descent update equations:'
    
    # build fake features
    def get_feature(surferID, hostID, couchrequestID):
        feat = np.zeros(3)
        if surferID==competitorset['winner']:
            feat[0] = 1 # later try 2,1 
        else: 
            feat[0] = -1
        feat[1] = 2
        return feat
    
    competitorset = {
        'hostID': 0,
        'list_surfers': [(1,1), (2,2), (3,3)],
        'winner': 3, # later try None
    }
    #print competitorset
    
    # init params
    dim = 3
    nhosts = 1
    theta = np.zeros(dim)
    r = 0
    r_hosts = np.zeros(nhosts) # do I need dictionary here: hostID -> param?
    
    # do a couple update steps
    for i in range(100):
                
        print "iteration", i
        print "\ttheta", theta
        print "\tr", r
        print "\tr_hosts", r_hosts
        print "\ttrue", competitorset['winner']
        print "\tpredicted", predict(theta, r, r_hosts, competitorset)
        
        theta, r, r_hosts = update(theta, r, r_hosts, competitorset, eta=0.1, regularization_lambda=0.1)
        
    