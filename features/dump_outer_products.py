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
  
  def __init__(self):
    sqler = Sqler()
    self.sq = sqler.db
    self.cursor = self.sq.cursor()
    self.fg = FeatureGetter()
    if os.path.exists('/home/tobibaum/'):
      self.req_table = 'couchrequest_tiny'
    else:
      self.req_table = 'couchrequest'
    self.dump_table = 'outer_products'
    self.request = "INSERT INTO "+self.dump_table+" (req_id, data) VALUES (%s, %s)"
    req_per_node = self.NUM_COUCHREQUESTS/comm_size 
    lower = comm_rank*req_per_node
    upper = req_per_node
    print 'node %d computes %d to %d'%(comm_rank, lower, upper)
    if comm_rank == comm_size-1:
      # The last guy just takes the rest
      upper *= 2
    # Get the req_ids for this node
    request = "SELECT id, host_user_id, surf_user_id FROM "+self.req_table+" limit "\
      + str(lower) + ", " + str(upper)
    self.cursor.execute(request)
    rows = self.cursor.fetchall()
    self.req_user_map = {int(row[0]):(int(row[1]),int(row[2])) for row in rows}
    #embed()
    
  def dump_outer_product(self, req_id, data):    
    thedata = cPickle.dumps(data)        
    try:
      self.cursor.execute(self.request, (req_id, thedata,))
    except:
      pass
#      import sys
      #print "Unexpected error:", sys.exc_info()[0]
 #     print 'req_id %d is already present'%req_id    
  
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
    for req_id in self.req_user_map.keys():
      print_it = False
      if commit_count == 100:
        self.commit()
        commit_count = 0
        print_it = True
      if print_it:
        print '%d computes id %d'%(comm_rank, req_id)
      t = time.time()
      data = self.get_features(req_id)
      
      self.dump_outer_product(req_id, data)
      t -= time.time()
      if print_it:
        print 'took %f sec'%(-t)
      total_time -= t
      counter += 1
      commit_count = 0

    print 'mean time: %f sec'%(total_time/float(counter))
    t = time.time()
    
    t -= time.time()
    print 'commit took %f sec'%(-t)
  
  def get_outer_product(self, req_id, vector_length):
    self.cursor.execute("select data from "+self.dump_table+" where req_id = "+str(req_id))
    result = cPickle.loads(self.cursor.fetchall()[0][0])
    res = np.zeros(vector_length)
    res[result]=1
    return res
  
def run():
  opd = OuterProductDumper()
  opd.execute()
  #opd.get_outer_product(1)  
  
if __name__=='__main__':
  run()
  
