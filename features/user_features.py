import cPickle
import numpy as np
import bucketizer
import os
import csrec_paths
import bucketizer
import re

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

    def init_dimensions(self):
        self.dimension = bucketizer.get_full_crossed_dimension(self.field_names)


    def verify_field_name(self, field_name):
        example_user = 1346062
        example_user_dct = self.user_data[example_user]
        if len(field_name)>1:
            if field_name in example_user_dct:
                return True
        print 'not found: ',field_name
        return False

    def init_field_names(self):
        f = open(csrec_paths.get_features_dir()+'relevant_features', 'rb')
        self.field_names = []
        if f:
            for line in f:
                line = re.sub(r'\s', '', line)
                if self.verify_field_name(line):
                    self.field_names.append(line)
        #print self.field_names
        example_user = 1346062
        example_user_dct = self.user_data[example_user]
        self.total_num_fields = len(example_user_dct)
        self.num_fields = len(self.field_names)
        #print self.num_fields

    def load_user_features_pkl(self):
        print 'loading user data...'
        self.user_data = cPickle.load(open(self.user_pklfile, 'rb'))
        print 'data for %s users loaded' % (len(self.user_data))

    def repair(self, user_dct):
        filler = {'field_type': int,
                  'field_data': 0}
        user_id = user_dct['user_id']
        for field in self.field_names:
            if field not in user_dct:
                #print 'warning user', user_id, 'missing field:', field
                user_dct[field] = filler

    def get_features(self, user_id, host_id, req_id):
        user1_dct = self.user_data[user_id]
        user2_dct = self.user_data[host_id]
        for user_dct in (user1_dct, user2_dct):
            if len(user_dct) != self.total_num_fields:
                #print 'warning missing features:', user_id
                self.repair(user_dct)
        return bucketizer.cross_bucketized_features(user1_dct, user2_dct, req_id,
                                                              self.dimension, self.field_names)
    
    def get_dimension(self):
        return self.dimension

def test():
    np.set_printoptions(threshold='nan')
    import time
    fg = FeatureGetter()
    t0 = time.time()
    arr = fg.get_features(1346062, 2722310, 1)
    run_time = time.time() - t0
    print arr
    print 'time to cross and expand feature:', (run_time)*1000, 'ms'
    print 'feature vec dimension', fg.get_dimension()
    print 'memory size of feature vector', arr.itemsize*fg.get_dimension(), 'bytes'

if __name__ == "__main__":
    test()
