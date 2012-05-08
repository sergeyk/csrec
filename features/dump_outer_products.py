from competitor_sets.Sqler import *
import cPickle
import MySQLdb
import random
from features.user_features import FeatureGetter
from features.pickle_user_data import pull_data_for_user

try:
  from IPython import embed
except ImportError:
  print 'ron'
from mpi.mpi_imports import *

class OuterProductDumper():
  
  NUM_COUCHREQUESTS = 10928173
  START_OFFSET = 0

  def __init__(self):
    sqler = get_sqler()
    self.sq = sqler.db
    self.cursor = self.sq.cursor()
    self.fg = FeatureGetter()
              
    self.dump_table = 'outer_products2'
    self.request = "INSERT INTO "+self.dump_table+" (req_id, data) VALUES (%s, %s)"
    req_per_node = self.NUM_COUCHREQUESTS/comm_size 
    lower = comm_rank*req_per_node + self.START_OFFSET
    upper = req_per_node
    print 'node %d computes %d to %d'%(comm_rank, lower, lower+upper)
    if comm_rank == comm_size-1:
      # The last guy just takes the rest
      upper *= 2
    # Get the req_ids for this node
    req = "SELECT req_id from " + self.dump_table
    self.cursor.execute(req)
    ids = self.cursor.fetchall()
    self.existent_req_ids = [int(x[0]) for x in ids]
    
    request = "SELECT id, host_user_id, surf_user_id FROM couchrequest limit "\
      + str(lower) + ", " + str(upper)
    print 'get the req_user_map database...'
    t = time.time()
    self.cursor.execute(request)
    t -= time.time()
    print 'took %f secs'%(-t)
    rows = self.cursor.fetchall()
    self.req_user_map = {int(row[0]):(int(row[1]),int(row[2])) for row in rows}
    print 'len user_map: %d'%len(self.req_user_map)
    for r in self.existent_req_ids:
      if self.req_user_map.has_key(r):
        self.req_user_map.pop(r)
    print 'reduced len user_map: %d'%len(self.req_user_map)
    #embed()
    
  def dump_outer_product(self, datas):
    try:        
      self.cursor.executemany(self.request, datas)
    except MySQLdb.IntegrityError:
      pass
  
  def commit(self):
    self.sq.commit()
    
  def get_dicts(self, req_id):
    user1 = self.req_user_map[req_id][0]
    dict1 = pull_data_for_user(self.cursor, user1)
    user2 = self.req_user_map[req_id][1]
    dict2 = pull_data_for_user(self.cursor, user2)
    return (dict1, dict2)
  
  def get_features(self, req_id):
    (dict1, dict2) = self.get_dicts(req_id)
    data = self.fg.get_features_from_dct(dict1, dict2, req_id)
    return np.nonzero(data)[0].tolist()
    
  def execute(self):
    total_time = 0
    counter = 0
    commit_count = 0
    all_keys = self.req_user_map.keys()
    datas = []
    for req_idx, req_id in enumerate(all_keys):
      t = time.time()
      
      data = self.get_features(req_id)
      
      #print 'took %f sec'%(-t)
      counter += 1
      
      #print '%d dumps 100 rows'%comm_rank
      thedata = cPickle.dumps(data)
      datas.append((req_id, thedata))      
      
      t -= time.time()
      if counter % 10000 == 0 or req_idx == len(all_keys)-1:
        print '%s finished %s/%s' % (comm_rank, counter, 
                                     len(self.req_user_map.keys()))

        self.dump_outer_product(datas)
        datas = []
      total_time -= t
      
    print 'mean time: %f sec'%(total_time/float(counter))
    t = time.time()
    
    t -= time.time()
    print 'commit took %f sec'%(-t)
    
def run():
  opd = OuterProductDumper()
  opd.execute()
  #opd.get_outer_product(1)  
  
if __name__=='__main__':
  run()
  
  
