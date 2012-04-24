''' Provide competitor sets for 
'''

import numpy as np
from Sqler import *

class CompetitorSet:
  
  def __init__(self, dict):
    # format all_rqsts: host_user_id, status, surf_user_id, id, rmd
    self.dict = dict
    
  def get_hostID(self):
    ''''''
    return int(self.dict[0]['host_id'])
  
  def get_surferlist(self):
    surf_list = []
    for r in self.dict:
      surf_list.append((int(r['surfer_id']), int(r['req_id'])))
    return surf_list
  
  def get_winner(self):
    winner = None
    for r in self.dict:
      if r['winner'] == 1:
        winner = int(r['surfer_id'])
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
  
  def __init__(self, validation=False):
    # TODO: Load the competitor sets and determine number of sets.
    self.sq = Sqler()
    if validation:
      self.db = 'competitor_sets_val'
    else:
      self.db = 'competitor_sets'
      
    self.num_sets = self.sq.rqst('select max(set_id) from '+self.db).fetch_row(1)[0][0]
    
  def get_nsamples(self):
    ''' Get the overall number of samples (= competitor sets) in our data'''
    return self.num_sets
  
  def get_sample(self, n):
    ''' Get an CompetitorSet object of the sample with index n'''
    res = self.sq.rqst('select * from '+self.db+' where set_id = '+str(n))
    rows = res.fetch_row(res.num_rows(),1)
    return CompetitorSet(rows) 
  

if __name__=='__main__':
  cs_coll = CompetitorSetCollection()
  print cs_coll.get_nsamples()
  cs = cs_coll.get_sample(43)
  print cs.get_hostID()
  print cs.get_surferlist()
  print cs.get_winner()
  

