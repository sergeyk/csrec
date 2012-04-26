import cPickle
import numpy as np
import math
import csrec_paths
from IPython import embed


class Bucketizer():
    def __init__(self):
        self.init_bucket_dividers()
        self.init_dimensions()

    def init_dimensions(self):
        self.dimension = 0
        self.base_dimensions = len(self.dividers_lol)
        for dividers_lst in self.dividers_lol:
            self.dimension += self.num_expanded_buckets(dividers_lst)

    def init_bucket_dividers(self):
        self.dividers_lol = cPickle.load(open(csrec_paths.get_dataset_dir()+'bucket_dividers.pkl', 'rb'))

    def cross_bucketized_features(self, user1_vec, user2_vec, req_vec):
        output = np.zeros(self.dimension, np.dtype(np.int32))
        offset = 0
        for i in range(len(user1_vec)):
            num_buckets = self.num_expanded_buckets(self.dividers_lol[i])
            bucket_i_1 = self.bucketize_feature(user1_vec[i], i)
            bucket_i_2 = self.bucketize_feature(user2_vec[i], i)
            true_index = offset + self.crossed_index(len(self.dividers_lol[i]), bucket_i_1, bucket_i_2)
            try:
              output[true_index] = 1
            except:
              embed()
            offset += num_buckets
        return output 
    
    def num_expanded_buckets(self, dividers_lst):
        return math.pow(len(dividers_lst)+1, 2)

    def bucketize_feature(self, feature_value, i):
        bucket_number = 0
        divider_lst = self.dividers_lol[i]
        for divider in divider_lst:
            if feature_value < divider:
                break;
            bucket_number += 1
        return bucket_number

    def crossed_index(self, num_buckets, i1, i2):
        return i1*num_buckets+i2

    def get_dimension(self):
        return self.dimension

    @classmethod
    def generate_bucket_dividers(cls,
                                 user_data_pkl_name = 'user_data.pkl',
                                 divider_name = 'bucket_dividers.pkl'):
        rows_lst = []
        print 'loading user data...'
        user_data = cPickle.load(open(csrec_paths.get_dataset_dir()+user_data_pkl_name, 'rb'))
        print 'data for %s users loaded' % (len(user_data))
        for user_id, features in user_data.iteritems():
            rows_lst.append(features)
        matrix = np.matrix(rows_lst)
        dividers = cls.find_matrix_dividers(matrix)
        cPickle.dump(dividers, open(divider_name, 'wb'))

    @classmethod
    def find_matrix_dividers(cls, m):
        out = np.mean(m, axis=0)
        out = np.squeeze(np.asarray(out))
        dividers = []
        for num in out:
            dividers.append([float(num)])
        return dividers

if __name__ == "__main__":
    #Bucketizer.generate_bucket_dividers()
    #Bucketizer.find_matrix_dividers(np.matrix([[1,2],[3,4]]))
    #Bucketizer.generate_bucket_dividers('sampled_user_data.pkl',
    #                                    'bucket_dividers.pkl')
    b = Bucketizer()
    a = np.ones(b.base_dimensions)
    b.cross_bucketized_features(a, a, None)
