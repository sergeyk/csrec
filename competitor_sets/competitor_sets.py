''' Provide competitor sets for 
'''

import numpy as np
from Sqler import *
from mpi.mpi_imports import *
import random
from IPython import embed 

class CompetitorSet:
  
  TRANS = {'host_id': 2, 'surfer_id':3, 'req_id':0, 'winner':4, 'set_id':1}
    
  def __init__(self, dict):
    # format all_rqsts: host_user_id, status, surf_user_id, id, rmd
    self.dict = dict

    
  def get_hostID(self):
    return int(self.dict[0][CompetitorSet.TRANS['host_id']])
  
  def get_surferlist(self):
    surf_list = []
    for r in self.dict:
      surf_list.append((int(r[CompetitorSet.TRANS['surfer_id']]), \
                        int(r[CompetitorSet.TRANS['req_id']])))
    return surf_list
  
  def get_winner(self):
    winner = None
    for r in self.dict:
      if int(r[CompetitorSet.TRANS['winner']]) == 1:
        winner = int(r[CompetitorSet.TRANS['surfer_id']])
        #print 'winner is', winner
        break
    return winner
  
  def get_winners(self):
    winners = []
    for r in self.dict:
      if r['winner'] == 1:
        winners.append(int(r['surfer_id']))
    if len(winners) == 0:
      winners = None
    return winners
  

class CompetitorSetCollection:
  ''' Storage of all competitor sets for all hosts. Load from dump, provide 
  CompetitorSet object'''
  
  NUM_TRAIN_SETS = 2954911 # Looked up and fix 
  
  def __init__(self, num_sets=100, mode = 'train'):
    ''' mode needs to be of train/test/val'''
    print 'start Sqler'
    self.sq = get_sqler()
    
    self.db = 'competitor_sets'          
    
    self.num_sets = num_sets # How much do we want
    if mode=='train':
      train_val_test = 1
    elif mode == 'val':
      train_val_test = 2
    elif mode == 'test':
      train_val_test = 3
    else:
      raise RuntimeError('Unknown mode %s in competitorSetColleciton'%mode)            
    train_val_test = str(train_val_test)
    
    if mode == 'train':
      request = "select set_id from competitor_sets where \
       train_val_test = 1"
      
    else:
      request = "select * from competitor_sets where train_val_test = " + \
        train_val_test
        
      if not self.num_sets == 'max':
        request += " limit 0, " +str(self.num_sets)
    
    print 'start loading competitor'
    res = self.sq.rqst(request, True)
    
    embed()       
    
    
    if mode == 'train' and not num_sets == 'max':
      random.seed(time.time())
      # ok this is it, we need to go random
      sets = []
      go_on = True
      entering = False
      last_set_id = -1
      while go_on:
        row = res.fetch_row(1,0)
        if row == ():
          go_on = False
          break
        set_id = row[1]
        if set_id == last_set_id:
          if entering:
            sets.append(row)
        else:
          # We see a new set_id. decide randomly whether to pick this.
          
    
    else:
      sets = res.fetch_row(11000000,0)
    last_set_id = sets[0][CompetitorSet.TRANS['set_id']]
    curr_set = []
    self.all_sets = []
    for cset in sets:
      curr_set_id = cset[CompetitorSet.TRANS['set_id']]
      
      if last_set_id == curr_set_id:
        curr_set.append(cset)
      else:
        self.all_sets.append(curr_set)
        curr_set = [cset]
        
      last_set_id = curr_set_id
    self.all_sets.append(curr_set)
    assert(len(sets) == sum([len(s) for s in self.all_sets]))
    assert(len(self.all_sets) <= self.num_sets)      
    self.num_sets = len(self.all_sets)
         
  def get_nsamples(self):
    ''' Get the overall number of samples (= competitor sets) in our data'''
    return self.num_sets
  
  def get_sample(self, n):
    ''' Get an CompetitorSet object of the sample with index n'''
    row = self.all_sets[n]
    return CompetitorSet(row)   
  
  def get_all_req_ids(self):
    req_ids = []
    for row in self.all_sets:
      for r in row:
        req_ids.append(r[CompetitorSet.TRANS['req_id']])
    return req_ids
  
  def get_req_ids_for_samples(self, ns):
    req_ids = []
    for n in ns:
      for r in self.all_sets[n]:
        req_ids.append(r[CompetitorSet.TRANS['req_id']])
    return req_ids

if __name__=='__main__':
  cs_coll_train = CompetitorSetCollection(num_sets=1000000)
  cs_coll_test = CompetitorSetCollection(num_sets=10000, mode='val')
  #cs_coll.get_user_dict("examplar_user_table")
  N = cs_coll_train.get_nsamples()
  N2 = cs_coll_test.get_nsamples()
  print N, N2
  cs = cs_coll_train.get_sample(random.randint(0,N-1))
  print cs.get_hostID()
  print cs.get_surferlist()
  print cs.get_winner()
