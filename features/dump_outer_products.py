from competitor_sets.Sqler import *
import cPickle
import MySQLdb
import random
from features.user_features import FeatureGetter
from features.pickle_user_data import pull_data_for_user
from IPython import embed

class OuterProductDumper():
  
  NUM_COUCHREQUESTS = 10928173
  
  def __init__(self):
    self.sq = MySQLdb.connect(db='CSRec')
    self.cursor = self.sq.cursor()
    self.request = "INSERT INTO outer_products (req_id, data) VALUES (%s, %s)"
    self.fg = FeatureGetter()
    self.table = 'couchrequest_tiny' 
    lower = 0
    upper = self.NUM_COUCHREQUESTS
    # Get the req_ids for this node
    request = "SELECT id, host_user_id, surf_user_id FROM "+self.table+" limit "\
      + str(lower) + ", " + str(upper)
    self.cursor.execute(request)
    rows = self.cursor.fetchall()
    self.req_user_map = {int(row[0]):(int(row[1]),int(row[2])) for row in rows}
    #embed()
    
  def dump_outer_product(self, req_id, data):    
    thedata = cPickle.dumps(data)        
    self.cursor.execute(self.request, (req_id, thedata,))  
  
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
    for req_id in self.req_user_map.keys():
      print 'compute id %d'%req_id
      t = time.time()
      data = self.get_features(req_id)
      
      self.dump_outer_product(req_id, data)
      t -= time.time()
      print 'took %f sec'%(-t)
      total_time -= t
      counter += 1
    print 'mean time: %f sec'%(total_time/float(counter))
    t = time.time()
    self.commit()
    t -= time.time()
    print 'commit took %f sec'%(-t)
  
  def get_outer_product(self, req_id):
    self.cursor.execute("select data from "+self.table+" where req_id = "+str(req_id))
  
def run():
  opd = OuterProductDumper()
  opd.execute()  
  
if __name__=='__main__':
  run()
  