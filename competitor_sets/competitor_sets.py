''' Provide competitor sets for 
'''

import numpy as np
from Sqler import *
from IPython import embed


class CompetitorSet:
  
  TRANS = {'host_id': 2, 'surfer_id':3, 'req_id':0, 'winner':4, 'set_id':1}
    
  def __init__(self, dict):
    # format all_rqsts: host_user_id, status, surf_user_id, id, rmd
    self.dict = dict

    
  def get_hostID(self):
    ''''''
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
  
  def __init__(self, num_sets=100, split_date='2011-03-29 11:41:04', testing=False, validation=False):
    self.sq = Sqler()
    if testing:
      if validation:
        self.db = 'competitor_sets_test_val'
      else:
        self.db = 'competitor_sets_test_train'
        
      res = self.sq.rqst('select * from '+self.db+' group by set_id;')
    else:
      # Otherwise we want to create a random subset of  
      self.db = 'competitor_sets'
          
      
      self.split_date = "'2011-03-29 11:41:04'" 
      self.num_sets = num_sets # How much do we want
      if validation:
        date_restrict = ">"
      else:
        date_restrict = "<"        
      date_restrict += self.split_date
      
      request = "select competitor_sets.* from competitor_sets join (select set_id \
       from competitor_sets  where date "+date_restrict+" group by set_id order \
       by rand() limit 0," +str(self.num_sets)+") as T on (competitor_sets.set_id = T.set_id) \
       order by set_id"
      
      res = self.sq.rqst(request)       
    
    sets = res.fetch_row(11000000,0)
    last_set_id = sets[0][CompetitorSet.TRANS['set_id']]
    print last_set_id
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
    self.num_sets = len(self.all_sets) 
            
  def get_nsamples(self):
    ''' Get the overall number of samples (= competitor sets) in our data'''
    return self.num_sets
  
  def get_sample(self, n):
    ''' Get an CompetitorSet object of the sample with index n'''
    row = self.all_sets[n]
    return CompetitorSet(row)   

if __name__=='__main__':
  cs_coll = CompetitorSetCollection()
  print cs_coll.get_nsamples()
  cs = cs_coll.get_sample(43)
  print cs.get_hostID()
  print cs.get_surferlist()
  print cs.get_winner()
  

