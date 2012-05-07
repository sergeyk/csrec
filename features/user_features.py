import cPickle
import numpy as np
import bucketizer
import os
import csrec_paths
import bucketizer
import re
from competitor_sets.Sqler import Sqler

DUMP_TABLE = 'outer_products'

class FeatureGetter():
    """ Generates crossed features given ids

    Requires:
    'user_data.pkl' and 'bucket_dividers.pkl' to be in the current directory'
    
    Attribues:
    bucketizer: a Bucketizer object initialized with 'bucket_dividers.pkl'
    user_data: dictionary of {user_id : user_features} initialized from
    'user_data.pkl'
    """

    def __init__(self, testing=True):
        if testing:
          self.DATA_FILE = 'sampled_user_data.pkl' #'user_data.pkl'
        else:
          self.DATA_FILE = 'user_data.pkl'
          
        if os.path.exists('/u/vis/'):
          if testing:
            self.user_pklfile = csrec_paths.get_features_dir()+'sampled_user_data.pkl'
          else:
            self.user_pklfile = '/u/vis/x1/tobibaum/user_data.pkl'
        else:
          self.user_pklfile = csrec_paths.get_features_dir()+self.DATA_FILE
        self.load_user_features_pkl()
        self.init_field_names()
        self.init_dimensions()
        self.init_outer_products()
        self.num_users_not_found = 0
        self.num_users_total = 0
        self.total_num_fields = 0

    def init_outer_products(self):
        sqler = Sqler()
        self.sq = sqler.db
        self.cursor = self.sq.cursor()

    def get_cached_feature(self, req_id):
        sql_cmd = "select data from "+DUMP_TABLE+" where req_id = "+str(req_id)
        self.cursor.execute(sql_cmd)
        res = np.zeros(self.get_dimension())
        results = self.cursor.fetchall()
        if len(results)>0:
            pkl_dump = results[0][0]
            result = cPickle.loads(pkl_dump)
            res[result]=1
        else:
            print req_id
            self.num_users_not_found += 1
            #print self.num_users_not_found,'/',self.num_users_total
        self.num_users_total += 1
        return res

    def init_dimensions(self):
        self.dimension = bucketizer.get_full_crossed_dimension(self.field_names)
        
    def init_field_names(self):
        f = open(csrec_paths.get_features_dir()+'relevant_features', 'rb')
        self.field_names = []
        if f:
            for line in f:
                line = re.sub(r'\s', '', line)
                if line:
                    self.field_names.append(line)
        self.num_fields = len(self.field_names)

    def is_correct_num_fields(self, dct):
        if self.total_num_fields == 0:
            return False
        else:
            if len(dct) == self.total_num_fields:
                return True
            else:
                return False

    def init_total_num_fields(self, num):
        print 'total_fields =',num
        self.total_num_fields = num

    def load_user_features_pkl(self):
        print 'loading user data...'
        self.user_data = {}
        print 'data for %s users loaded' % (len(self.user_data))

    def repair(self, user_dct):
        filler = {'field_type': int,
                  'field_data': 0}
        # This is pretty bad if user_id is not in the dct...
        if 'user_id' not in user_dct: 
            user_dct['user_id'] = filler
        for field in self.field_names:
            if field not in user_dct:
                user_dct[field] = filler
        if self.total_num_fields == 0:
            self.init_total_num_fields(len(user_dct))

    def get_features_from_dct(self, user1_dct, user2_dct, req_id):
        for user_dct in (user1_dct, user2_dct):
            if not self.is_correct_num_fields(user_dct):
                self.repair(user_dct)
        return bucketizer.cross_bucketized_features(user1_dct, user2_dct, req_id,
                                                    self.dimension, self.field_names)

    def get_features_from_id(self, user_id, host_id, req_id):
        user1_dct = self.user_data[user_id]
        user2_dct = self.user_data[host_id]
        return self.get_features_from_dct(user1_dct, user2_dct, req_id)
    
    def get_features(self, user_id, host_id, req_id):
        return self.get_cached_feature(req_id)
    
    def get_dimension(self):
        return self.dimension

def test():
    np.set_printoptions(threshold='nan')
    import time
    fg = FeatureGetter()
    t0 = time.time()
    arr = fg.get_features(1346062, 2722310, 1)
    run_time = time.time() - t0
    #print arr
    print 'time to cross and expand feature:', (run_time)*1000, 'ms'
    print 'feature vec dimension', fg.get_dimension()
    print 'memory size of feature vector', arr.itemsize*fg.get_dimension(), 'bytes'

if __name__ == "__main__":
    test()
