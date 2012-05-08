''' Provide competitor sets for
'''

import numpy as np
from Sqler import *
from mpi.mpi_imports import *
import random
from IPython import embed 
import time
import csrec_paths
import matplotlib.pyplot as plt

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
  
  def __init__(self, num_sets='max', mode = 'train', size_comp_sets=2):
    ''' 
    mode needs to be of train/test/test_win/val
    size_comp_sets determines the size of each competitor_set using test_win
    '''
    print 'start Sqler'
    self.sq = get_sqler()
    
    self.db = 'competitor_sets'          
    
    self.num_sets = num_sets # How much do we want
    if mode=='train':
      train_val_test = 1
    elif mode == 'val':
      train_val_test = 2
    elif mode == 'test' or mode == 'test_win':
      train_val_test = 3
    else:
      raise RuntimeError('Unknown mode %s in competitorSetColleciton'%mode)            
    train_val_test = str(train_val_test)
    
    if mode == 'train':
      if num_sets == 'max':
        request = "select * from competitor_sets where \
         train_val_test = 1"
      else:
        set_filename = os.path.join(csrec_paths.ROOT, 'competitor_sets', 'all_set_ids')
        if not os.path.exists(set_filename):
          set_ids_req = "select distinct set_id from competitor_sets where train_val_test=1"
          print 'read the set_ids'
          res = self.sq.rqst(set_ids_req)
          set_ids = res.fetch_row(11000000,0)
          set_ids = [int(x[0]) for x in set_ids]
          cPickle.dump(set_ids, open(set_filename, 'w'))
          print 'pickled the set_ids'
        else:
          set_ids = cPickle.load(open(set_filename, 'r'))
          
        smaller_set_ids = np.random.permutation(len(set_ids)).tolist()[:self.num_sets]
        #smaller_set_ids = np.random.random_integers(0,len(set_ids)-1,self.num_sets).tolist()
        
        base_string = "select * from competitor_sets where set_id in ("
        sets = []
        counter = 0
        set_req = base_string
        add_string = "%d,"
        for s_idx, s in enumerate(smaller_set_ids):
          set_req += add_string%s
          counter += 1
          if counter == 100000 or s_idx == len(smaller_set_ids)-1:
            counter = 0
            set_req = set_req[:-1]+')' # remove last 'or'
            t_db = time.time()
            cursor = self.sq.db.cursor()
            cursor.execute(set_req)
            sets += cursor.fetchall()
            set_req = base_string
        
        t_db -= time.time()
  #      print 'db lookup for compset took %f sec'%-t
                 
    else:
      request = "select * from competitor_sets where train_val_test = " + \
        train_val_test        
               
      
      if mode == 'test_win':
        # We want just competitorsets with a winner in it.
        # this is for sets with 1 or more surfers
#        request = "select * from competitor_sets where train_val_test = " + \
#          train_val_test + " and winner_set=1"
        request = "select * from competitor_sets join (select * from \
          (select *, count(winner) as cnt from competitor_sets where \
          train_val_test="+train_val_test+" and winner_set=1 group by set_id) \
          as t where cnt > "+str(size_comp_sets)+") as TT on (TT.set_id = \
          competitor_sets.set_id)"  
      if not self.num_sets == 'max':
        request += " limit 0, " +str(self.num_sets)

      print 'start loading competitor'
      res = self.sq.rqst(request, True)
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
  t = time.time()
  comp_set_sizes = np.zeros(10)
  for i in range(10):
    cs_coll_train = CompetitorSetCollection(mode='test_win', size_comp_sets=i)
    comp_set_sizes[i] = cs_coll_train.get_nsamples()
  plt.plot(comp_set_sizes)
  plt.show()