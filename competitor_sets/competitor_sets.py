''' Provide competitor sets for 
'''

import numpy as np
from Sqler import *
from IPython import embed
from mpi.mpi_imports import *

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
  
  def __init__(self, num_sets=100, split_date='2011-08-16 16:24:47', testing=False, validation=False, just_winning_sets = False):
    self.sq = Sqler()
    if testing:
      if validation:
        self.db = 'competitor_sets_test_val'
      else:
        self.db = 'competitor_sets_test_train'
      
      if just_winning_sets:
        res = self.sq.rqst("SELECT * FROM `competitor_sets` where winner=1 group by set_id")
      else:    
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
      
      ###### ASSUMPTION: For now assume, that we only have one active table at a time
      self.set_ids_table_name = "temp_set_ids_%d"%comm_rank
      self.sq.rqst("drop table if exists "+self.set_ids_table_name)
              
      ## Now create this table with:
      if just_winning_sets:
        cr_tab_request = "create table "+self.set_ids_table_name+" as (select set_id \
         from competitor_sets  where date "+date_restrict+" where winner=1 group by set_id order \
         by rand() limit 0, " +str(self.num_sets)+" );"      
        
      else:
        cr_tab_request = "create table "+self.set_ids_table_name+" as (select set_id \
         from competitor_sets  where date "+date_restrict+" group by set_id order \
         by rand() limit 0, " +str(self.num_sets)+" );"      
      
      res = self.sq.rqst(cr_tab_request)
      
      # create the users table. First a table with two columns for host/surfer
      self.user_table_name = "temp_users_table_%d"%comm_rank
      self.sq.rqst("drop table if exists "+self.user_table_name)
      self.sq.rqst("drop table if exists "+self.user_table_name+"temp")
      self.sq.rqst("create table " +self.user_table_name+ "temp as(SELECT host_id, surfer_id FROM "+self.set_ids_table_name+" join \
        competitor_sets on ( " + self.set_ids_table_name + ".set_id = competitor_sets.set_id))")
      
      # then both in one column
      #create table a as (select * from (SELECT distinct host_id as user_id FROM TT union select surfer_id from TT) as T)
      self.sq.rqst("create table " +self.user_table_name+ " as( select * from (SELECT distinct host_id \
        as user_id FROM "+self.user_table_name+"temp union select surfer_id from " +self.user_table_name+"temp) as T)")
      # drop the old unneeded table  
      self.sq.rqst("drop table "+self.user_table_name+"temp")
      # and create an index on the user_ids.
      self.sq.rqst("create index ind using BTREE on "+self.user_table_name+" (user_id ASC)")
        
      request = "select competitor_sets.* from competitor_sets join " + \
        self.set_ids_table_name + " on (competitor_sets.set_id = "+self.set_ids_table_name+".set_id) \
        order by set_id"
      res = self.sq.rqst(request)       
    
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
    self.num_sets = len(self.all_sets)
    
    # Drop the set_id table (we are just interested in the user id table from 
    # now on
    if not testing:
      self.sq.rqst("drop table %s"%(self.set_ids_table_name))
    
    # We just want sets where we actually observe a winner. 
    #if just_winning_sets:
       
  
  def get_user_dict(self, table):
    '''
    For each competitor_set we have a fixed set of users. Get the Features for 
    all of 'em with one DB lookup.
    '''
    request = "SELECT "+table+".* FROM "+table+" join "+self.user_table_name+ \
      " on ("+table+".user_id = "+self.user_table_name+".user_id)"
    dbres = self.sq.rqst(request)
    res = dbres.fetch_row(11000000)
    ress = {}
    for r in res:
      r = np.array(r)
      r[np.where(r == None)] = 0
      ress[int(r[0])] = r
    # And we erase that table
    self.sq.rqst("drop table "+self.user_table_name)
    return ress
  
  def get_nsamples(self):
    ''' Get the overall number of samples (= competitor sets) in our data'''
    return self.num_sets
  
  def get_sample(self, n):
    ''' Get an CompetitorSet object of the sample with index n'''
    row = self.all_sets[n]
    return CompetitorSet(row)   

if __name__=='__main__':
  cs_coll = CompetitorSetCollection()
  cs_coll.get_user_dict("examplar_user_table")
  print cs_coll.get_nsamples()
  cs = cs_coll.get_sample(43)
  print cs.get_hostID()
  print cs.get_surferlist()
  print cs.get_winner()
  

