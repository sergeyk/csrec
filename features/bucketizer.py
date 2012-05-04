import cPickle
import numpy as np
import math
import csrec_paths
import feature_processor
import pprint

class Bucketizer():
    def __init__(self):
        self.init_bucket_dividers()
        self.init_dimensions()
        
    def init_dimensions(self):
        self.dimension = 0
        self.base_dimensions = len(self.dividers_lol)
        for field_name, dividers_lst in self.dividers_lol.iteritems():
            self.dimension += self.num_expanded_buckets(dividers_lst)

    def init_bucket_dividers(self):
        self.dividers_lol = cPickle.load(open(csrec_paths.get_features_dir()+'bucket_dividers.pkl', 'rb'))

    def cross_bucketized_features(self, user1_vec, user2_vec, req_vec):
        output = np.zeros(self.dimension, np.dtype(np.int32))
        offset = 0
        c = feature_processor.Converter
        
        i = 0
        for field_name in user1_vec:
            num_buckets = self.num_expanded_buckets(self.dividers_lol[field_name])
            bucket_i_1 = self.bucketize_feature(c.convert(field_name, user1_vec[field_name]), field_name)
            bucket_i_2 = self.bucketize_feature(c.convert(field_name, user2_vec[field_name]), field_name)
            true_index = offset + self.crossed_index(len(self.dividers_lol[field_name]), bucket_i_1, bucket_i_2)
            output[true_index] = 1
            offset += num_buckets
            i += 1
        return output
    
    def num_expanded_buckets(self, dividers_lst):
        return math.pow(len(dividers_lst)+1, 2)

    def bucketize_feature(self, feature_value, field_name):
        bucket_number = 0
        divider_lst = self.dividers_lol[field_name]
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
                                 user_data_pkl_name='sampled_user_data.pkl',
                                 divider_name='bucket_dividers.pkl',
                                 num_buckets=10):
        rows_lst = []
        print 'loading user data...'
        user_data = cPickle.load(open(csrec_paths.get_features_dir()+user_data_pkl_name, 'rb'))
        print 'data for %s users loaded' % (len(user_data))
        all_values = cls.find_all_values_of_cols(user_data)
        bucket_dividers = {}
        for field_name, possible_values in all_values.iteritems():
            bucket_dividers[field_name] = cls.get_dividers_from_values(possible_values, num_buckets)
#        pprint.pprint(bucket_dividers)
        cPickle.dump(bucket_dividers, open(csrec_paths.get_features_dir()+divider_name, 'wb'))

    @classmethod
    def get_dividers_from_values(cls, possible_values, max_buckets):
        uniques = set(possible_values)
        num_unique = len(uniques)
        if num_unique < max_buckets:
            return sorted(list(uniques))
        else:
            sorted_values = sorted(possible_values)
            return sorted(list(set(sorted_values[0:-1:len(sorted_values)/max_buckets])))
            
    @classmethod
    def find_all_values_of_cols(cls, user_data_dct):
        all_values = {}
        c = feature_processor.Converter
        i = 0
        for user_id, data_dct in user_data_dct.iteritems():
            i += 1
            for field_name, field_dct in data_dct.iteritems():
                if field_name not in all_values:
                    all_values[field_name] = []
                all_values[field_name].append(c.convert(field_name, field_dct))
            if i%1000 == 0:
                print "%s/%s" % (i, len(user_data_dct)), 'users finished'
           
        for field_name, field_values in all_values.iteritems():
            print 'number of different values for', field_name, len(set(field_values))
        
        return all_values
        
if __name__ == "__main__":
    Bucketizer.generate_bucket_dividers()
    #b = Bucketizer()
    #a = np.ones(b.base_dimensions)
    #b.cross_bucketized_features(a, a, None)
