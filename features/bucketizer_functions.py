BUCKETIZER_FN_FOR_FIELDS = {}

def cross_bucketized_features(user1_dct, user2_dct, req_dct, 
                              dividers, feature_dimension):
    
    crossed_feature_vector = np.zeros(feature_dimension, np.dtype(np.int32))
    cur_feature_offset = 0
    c = feature_processor.Converter
    
    for field_name in user1_dct:
        bucketizer_fn = get_bucketizer_fn(field_name)
        num_buckets = bucketizer_fn.num_buckets_after_cross(field_name)
        bucketed_1 = bucketizer_fn.bucketize(field_name,
            c.convert(field_name, user1_dct[field_name]))
        bucketed_2 = bucketizer_fn.bucketize(field_name,
            c.convert(field_name, user2_dct[field_name]))
        crossed_bucket_index = cur_feature_offset + crossed_index(
            len(dividers[field_name]), 
            bucket_i_1, bucket_i_2)
        crossed_feature_vector[crossed_bucket_index] = 1
        cur_feature_offset += num_buckets
        return crossed_feature_vector

def crossed_index(num_buckets, i1, i2):
    return i1*num_buckets+i2

def get_bucketizer_fn(field_name):
    if field_name in BUCKETIZER_FN_FOR_FIELDS:
        return BUCKETIZER_FN_FOR_FIELDS[field_name]
    else:
        return BaseBucketizerFn

class BaseBucketizerFn(object):
    @classmethod
    def num_buckets_after_cross(cls):
        return math.pow(len(dividers)+1, 2)

    @classmethod
    def bucketize(cls, feature_value, field_name):
        bucket_number = 0
        divider_lst = dividers[field_name]
        for divider in divider_lst:
            if feature_value < divider:
                break;
            bucket_number += 1
            return bucket_number
