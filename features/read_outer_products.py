'''
Module to speed it up once again.
Instead of reading the features one at a time, we 
'''
import numpy as np
import cPickle
from competitor_sets.Sqler import Sqler
import time

class OuterProducGetter():
  
  DUMP_TABLE = 'outer_products'
  RQST_LENGTH_TRESH = 3000
  
  def __init__(self, dimension):
    self.dimension = dimension
    self.outer_products = {}
    self.init_db()
    
  def init_db(self):
    sqler = Sqler()
    self.sq = sqler.db
    self.cursor = self.sq.cursor()
        
  def get_product(self, req_id):
    feat = np.zeros(self.dimension)
    r = self.outer_products[req_id]
    feat[r] = 1
    return feat
  
  def recreate_outer_prods_from_req_ids(self, req_ids):
    self.outer_products = {}
    self.create_outer_prods_from_req_ids(req_ids)
    
  def create_outer_prods_from_req_ids(self, req_ids):
    '''
    We expect a list of request ids and will split them into readable chunks 
    '''
    #print 'create outer products for %d requests'%len(req_ids)
    sql_cmd_extens = " or req_id = %d "
    sql_cmd_base = "select req_id, data from "+self.DUMP_TABLE+" where req_id = %d "
    print 'create outer products from req ids...'
    t = time.time()
    req_len_cnter = 0
    first_elem = True
    last_elem = False
    for req_idx, req_id in enumerate(req_ids):
      if req_idx == len(req_ids)-1:
        last_elem = True
      req_len_cnter += 1      
      if first_elem:
        sql_cmd = sql_cmd_base%req_id
        first_elem = False
        continue
        
      sql_cmd += sql_cmd_extens%req_id
      if req_len_cnter > self.RQST_LENGTH_TRESH or last_elem:
        sql_cmd += ";"
        #print 'process id %d'%req_id
        # Now the command is big enough and we execute it
        t = time.time()     
        self.cursor.execute(sql_cmd)
        results = self.cursor.fetchall()
        t -= time.time()
        #print 'Res for this request: ', len(results)
        for res in results:
          #print 'convert req_id %d'%res[0]
          pkl_dump = res[1]
          try:
            r = cPickle.loads(pkl_dump)
          except:
            print 'what?'
            return
            
          self.outer_products[res[0]] = r
        req_len_cnter = 0
        first_elem = True
    t -= time.time()
    print '\t creating outer prods took %f secs'%-t
          
if __name__=='__main__':
  # get the damn req_ids
  sq = Sqler()
  cursor = sq.db.cursor()
  cursor.execute("Select id from couchrequest limit 0,500000")
  req_ids = cursor.fetchall()
  req_ids = [int(x[0]) for x in req_ids]
  opg = OuterProducGetter(4000)
  t = time.time()
  opg.create_outer_prods_from_req_ids(req_ids)
  t -= time.time()
  print 'the whole reading took %f'%-t
  
  
  
  
   
          