'''
Create and Read the user dictionaries
'''

import cPickle
from competitor_sets.Sqler import get_sqler
import os
import csrec_paths
import time
from IPython import embed

class UserDictionaries():
  def __init__(self, threshold=0.75, force=False):
    self.dict_file = os.path.join(csrec_paths.get_dataset_dir(),'baseline_feat_dict')
    self.threshold = threshold
    sq = get_sqler()
    self.cursor = sq.db.cursor()
    self.features = ['priority', 'priority2', 'vouched', 'references_count', 
      'friend_link_count', 'references_to_count']
    if os.path.exists(self.dict_file) and not force:
      print 'load user baseline dictionary from %s'%self.dict_file
      self.dict = cPickle.load(open(self.dict_file, 'r'))
    else:
      self.dict = {}
      self.create_dictionary()
      cPickle.dump(self.dict, open(self.dict_file, 'w'))    
    
    self.thresh_file = os.path.join(csrec_paths.get_dataset_dir(),'baseline_feat_threshs_'+str(self.threshold))
    if  os.path.exists(self.thresh_file) and not force:
      self.threshs = cPickle.load(open(self.thresh_file, 'r'))
    else:
      self.threshs = []
      self.create_threshs()
      cPickle.dump(self.threshs, open(self.thresh_file, 'w'))
    
  def get_dictionary_for_user(self, user_id):
    return self.dict[user_id]
  
  def get_thresh_val_for_feat(self, feature):
    if type(feature) == type("string"):
      ind = self.features.index(feature)
    else:
      ind = feature
    return self.threshs[ind]
  
  def create_dictionary(self):
    print 'create the dictionary'
        
    req = "SELECT user_id "
    for f in self.features:
      req += ", %s "%f
    req += " from user_small "
    t = time.time()
    print req
    self.cursor.execute(req)
    res = self.cursor.fetchall()
    t -= time.time()
    print 'db request took %f'%-t
    for r in res:
      self.dict[r[0]] = r[1:]
  
  def create_threshs(self):
    t = time.time()
    print 'get the number of rows...'
    self.cursor.execute("select count(*) from user_small")
    num_rows = self.cursor.fetchall()
    t -= time.time()
    print '\ttook %f'%-t
    pick_elem = int(int(num_rows[0][0])*self.threshold)
    for f in self.features:
      print 'computing thresh for %s'%f
      t = time.time()
      self.cursor.execute("select "+f+" from user_small order by "+f+" limit "+str(pick_elem)+", 1")      
      res = self.cursor.fetchall()[0][0]
      print 'thresh:', res
      self.threshs.append(res)
      t -= time.time()
      print 'db request took %f'%-t
      
if __name__=='__main__':
  ud = UserDictionaries(force=True)
  #ud.create_dictionary()
  embed()
  ud.get_dictionary_for_user(8)
  