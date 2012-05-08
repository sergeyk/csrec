import cPickle
import numpy as np
import bucketizer
import os
import csrec_paths
import bucketizer
import re
from competitor_sets.Sqler import Sqler
from features.read_outer_products import OuterProducGetter

NUM_FEATURES = 138

class FeatureGetter():
    """ Generates crossed features given ids

    Requires:
    'user_data.pkl' and 'bucket_dividers.pkl' to be in the current directory'
    
    Attribues:
    bucketizer: a Bucketizer object initialized with 'bucket_dividers.pkl'
    user_data: dictionary of {user_id : user_features} initialized from
    'user_data.pkl'
    """

    def __init__(self, testing=False):
        if testing:
            DATA_FILE = 'sampled_user_data.pkl'
            self.user_pklfile = csrec_paths.get_features_dir() +DATA_FILE
            self.load_user_features_pkl()
        self.init_field_names()
        self.init_dimensions()
        self.num_users_not_found = 0
        self.num_users_total = 0
        self.total_num_fields = 0
        self.testing = testing
        self.outer_product_getter = OuterProducGetter(self.dimension)

    def get_cached_feature(self, req_id):
        return self.outer_product_getter.get_product(req_id)  
          
    def upt_out_prod_get(self, req_ids):
        #print 'initialize outer prods'        
        self.outer_product_getter.create_outer_prods_from_req_ids(req_ids)
        
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
        if NUM_FEATURES != num:
            raise Exception("Ron: Error %s features expected, %s seen in the example user" % (NUM_FEATURES, num))
        self.total_num_fields = num

    def load_user_features_pkl(self):
        self.user_data = cPickle.load(open(self.user_pklfile, 'rb'))
        print 'FG RUNNING IN TEST MODE: data for %s users loaded' % (len(self.user_data))

    def repair(self, user_dct):
        filler = {'field_type': int,
                  'field_data': 0}
        # Lol there are users without user ids...
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

    def get_features_from_ids(self, user_id, host_id, req_id):
        user1_dct = self.user_data[user_id]
        user2_dct = self.user_data[host_id]
        return self.get_features_from_dct(user1_dct, user2_dct, req_id)
    
    def get_features(self, user_id, host_id, req_id):
        if self.testing:
            return self.get_features_from_ids(user_id, host_id, req_id)
        else:
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
