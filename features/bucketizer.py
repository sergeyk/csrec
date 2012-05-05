import cPickle
import csrec_paths
import math
import feature_processor
import numpy as np

BUCKETIZER_FN_FOR_FIELD = {}
DEFAULT_DIVIDERS = cPickle.load(open(csrec_paths.get_features_dir()+'bucket_dividers.pkl', 'rb'))

def cross_bucketized_features(user1_dct, user2_dct, req_dct, 
                              feature_dimension, field_names):
    cur_feature_offset = 0
    c = feature_processor.Converter
    crossed_feature_vector = np.zeros(feature_dimension, np.dtype(np.int32))

    for field_name in field_names:
        bucketizer_fn = get_bucketizer_fn(field_name)
        num_crossed_buckets = bucketizer_fn.post_cross_dim(field_name)
        bucket_idx1 = bucketizer_fn.get_bucket_idx(field_name,
                                                   c.convert(field_name, user1_dct[field_name]))
        bucket_idx2 = bucketizer_fn.get_bucket_idx(field_name,
                                                   c.convert(field_name, user2_dct[field_name]))
        crossed_bucket_idx = cur_feature_offset + \
            crossed_index(bucketizer_fn.pre_cross_dim(field_name), 
                          bucket_idx1, bucket_idx2)
        cur_feature_offset += num_crossed_buckets
        crossed_feature_vector[crossed_bucket_idx] = 1
    return crossed_feature_vector

def crossed_index(num_buckets, i1, i2):
    return i1*num_buckets+i2

def get_bucketizer_fn(field_name):
    if field_name in BUCKETIZER_FN_FOR_FIELD:
        return BUCKETIZER_FN_FOR_FIELD[field_name]
    else:
        return DefaultBucketizerFn

def get_full_crossed_dimension(field_names_lst):
    dimension = 0
    for field_name in field_names_lst:
        fn = get_bucketizer_fn(field_name)
        dimension += fn.post_cross_dim(field_name)
    return dimension

class DefaultBucketizerFn(object):
    
    @classmethod
    def pre_cross_dim(cls, field_name):
        return (len(DEFAULT_DIVIDERS[field_name]) + 1)

    @classmethod
    def post_cross_dim(cls, field_name):
        return math.pow(len(DEFAULT_DIVIDERS[field_name])+1, 2)

    @classmethod
    def get_bucket_idx(cls, field_name, feature_value):
        bucket_idx = 0
        dividers_lst = DEFAULT_DIVIDERS[field_name]
        for divider in dividers_lst:
            if feature_value < divider:
                break;
            bucket_idx += 1
        return bucket_idx
