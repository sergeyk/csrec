''' Provide competitor sets for 
'''

import numpy as np
from Sqler import *
from mpi.mpi_imports import *
import random

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
  
  def __init__(self, num_sets=100, split_date='2011-08-16 16:24:47', testing=False, validation=False, just_winning_sets = False):
    print 'start Sqler'
    t = time.time()
    self.sq = Sqler()
    t -= time.time()
    print 'took %f secs'%-t
    
    if testing:
      if validation:
        self.db = 'competitor_sets_test_val'
      else:
        self.db = 'competitor_sets_test_train'
      
      if just_winning_sets:
        res = self.sq.rqst("select "+self.db+".* from "+self.db+" join (select set_id from (select set_id, count(winner) as \
          cnt, sum(winner) as sum from "+self.db+" group by set_id)as t where \
          cnt >1 and sum > 0) as TT on ("+self.db+".set_id = TT.set_id);")
        
      else:    
        res = self.sq.rqst('select * from '+self.db+' group by set_id;')
    else: 
      self.db = 'competitor_sets'          
      
      self.split_date = split_date
      self.num_sets = num_sets # How much do we want
      if validation:
        date_restrict = "> "
      else:
        date_restrict = "< "        
      date_restrict += "'"+self.split_date+"'"
      
              
      if just_winning_sets:
# select set_id from (select set_id, count(winner) as cnt, sum(winner) as 
# sum from competitor_sets group by set_id)as t where cnt >1 and sum > 0;
        self.set_ids_table = "select set_id from \
         (select set_id, count(winner) as cnt, sum(winner) as sum \
         from competitor_sets  where date "+date_restrict+" group by set_id order \
         by rand()  ) as T where cnt > 1 and sum > 0"      
        
      else:
        self.set_ids_table = "select set_id \
         from competitor_sets  where date "+date_restrict+" group by set_id order \
         by rand()"
      
      if not self.num_sets == 'max':
        self.set_ids_table += "limit 0, " +str(self.num_sets)
            
      request = "select competitor_sets.* from competitor_sets join (" + \
        self.set_ids_table + ") as T on (competitor_sets.set_id = T.set_id) \
        order by set_id"
      
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
  cs_coll_train = CompetitorSetCollection(num_sets=10000)
  cs_coll_test = CompetitorSetCollection(num_sets=10000, validation=True)
  #cs_coll.get_user_dict("examplar_user_table")
  N = cs_coll_train.get_nsamples()
  N2 = cs_coll_test.get_nsamples()
  print N, N2
  cs = cs_coll_train.get_sample(random.randint(0,N-1))
  print cs.get_hostID()
  print cs.get_surferlist()
  print cs.get_winner()
  

