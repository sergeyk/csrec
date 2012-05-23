import cPickle
import csrec_paths
import math
import numpy as np
import test_bucketizer
import bucketizer_fn as bf

def cross_bucketized_features(user1_dct, user2_dct, req_dct, 
                              feature_dimension, field_names, debug=False):
    cur_feature_offset = 0
    crossed_feature_vector = np.zeros(feature_dimension, np.dtype(np.int32))
    debug_info = []

    for field_name in field_names:
        bucketizer_fn = get_bucketizer_fn(field_name)
        bucket_idx1_lst = bucketizer_fn.get_bucket_idx(field_name,
                                                   user1_dct[field_name])
        bucket_idx2_lst = bucketizer_fn.get_bucket_idx(field_name,
                                                   user2_dct[field_name])
        crossed_idx_lst = []
        for bucket_idx1 in bucket_idx1_lst:
            for bucket_idx2 in bucket_idx2_lst:
                crossed_idx_lst.append(crossed_index(
                        bucketizer_fn.pre_cross_dim(field_name), 
                        bucket_idx1, bucket_idx2))
        offset_crossed_bucket_idx = cur_feature_offset
        offset_bucket_idx1 = (offset_crossed_bucket_idx +
                              bucketizer_fn.post_cross_dim(field_name))
        offset_bucket_idx2 = (offset_bucket_idx1 +
                              bucketizer_fn.pre_cross_dim(field_name))
                                             
        activated_idx_lst = []
        for bucket_idx1 in bucket_idx1_lst:
            activated_idx_lst.append(offset_bucket_idx1 + bucket_idx1)
        for bucket_idx2 in bucket_idx2_lst:
            activated_idx_lst.append(offset_bucket_idx2 + bucket_idx2)
        for crossed_idx in crossed_idx_lst:
            activated_idx_lst.append(offset_crossed_bucket_idx + crossed_idx)

        for activated_idx in activated_idx_lst:
            crossed_feature_vector[activated_idx] = 1
        
        cur_feature_offset += bucketizer_fn.final_dim(field_name)

    if debug:
        test_bucketizer.test(crossed_feature_vector, user1_dct, user2_dct, 
                             req_dct, feature_dimension, field_names)
    return crossed_feature_vector

def crossed_index(num_buckets, i1, i2):
    return i1*num_buckets+i2

def get_bucketizer_fn(field_name):
    if field_name in bf.BUCKETIZER_FN_FOR_FIELD:
        return bf.BUCKETIZER_FN_FOR_FIELD[field_name]
    else:
        return bf.DEFAULT_BUCKETIZER_FN

def get_full_crossed_dimension(field_names_lst):
    dimension = 0
    for field_name in field_names_lst:
        fn = get_bucketizer_fn(field_name)
        post_len = fn.final_dim(field_name)
        dimension += post_len
    print 'dimension of features = %s' % dimension
    return dimension
