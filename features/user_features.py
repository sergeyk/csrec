import cPickle
import numpy as np
import bucketizer
import os

import csrec_paths

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
        self.init_bucket_dividers()
        self.init_dimensions()
        self.init_field_names()

    def init_dimensions(self):
        self.dimension = 0
        self.base_dimensions = len(self.dividers)
        for field_name, dividers_lst in self.dividers.iteritems():
            self.dimension += self.num_expanded_buckets(dividers_lst)

    def init_field_names(self):
        example_user_dct = self.user_data[1346062]
        self.field_names = example_user_dct.keys()

    def init_bucket_dividers(self):
        self.dividers = cPickle.load(open(csrec_paths.get_features_dir()+'bucket_dividers.pkl', 'rb'))

    def load_user_features_pkl(self):
        print 'loading user data...'
        self.user_data = cPickle.load(open(self.user_pklfile, 'rb'))
        print 'data for %s users loaded' % (len(self.user_data))

    def get_features(self, user_id, host_id, req_id):
        user_features = self.user_data[user_id]
        host_features = self.user_data[host_id]
        return bucketizer_functions.cross_bucketized_features(user1_dct, user2_dct, request,
                                                              self.dimension, self.field_names)
    
    def get_dimension(self):
        return self.bucketizer.get_dimension()

def test():
    np.set_printoptions(threshold='nan')
    import time
    fg = FeatureGetter()
    t0 = time.time()
    arr = fg.get_features(1346062, 2722310, 1)
    run_time = time.time() - t0
    print arr
    print 'time to cross and expand feature:', (run_time)*1000, 'ms'
    print 'feature dimension', fg.get_dimension()
    print 'memory size of feature vector', arr.itemsize*fg.get_dimension(), 'bytes'

if __name__ == "__main__":
    test()
