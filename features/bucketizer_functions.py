BUCKETIZER_FN_FOR_FIELDS = {}

def cross_bucketized_features(user1_dct, user2_dct, req_dct, 
                              feature_dimension, field_names):
    cur_feature_offset = 0
    c = feature_processor.Converter
    crossed_feature_vector = np.zeros(feature_dimension, np.dtype(np.int32))

    for field_name in field_names:
        bucketizer_fn = get_bucketizer_fn(field_name)
        num_buckets = bucketizer_fn.num_buckets_after_cross(field_name)
        bucketed_1 = bucketizer_fn.get_bucket_idx(field_name,
            c.convert(field_name, user1_dct[field_name]))
        bucketed_2 = bucketizer_fn.get_bucket_idx(field_name,
            c.convert(field_name, user2_dct[field_name]))
        crossed_bucket_idx = cur_feature_offset + crossed_index(
            len(dividers[field_name]), 
            bucket_i_1, bucket_i_2)
        cur_feature_offset += num_buckets
        crossed_feature_vector[crossed_bucket_idx] = 1
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
    def num_buckets_after_cross(cls, field_name):
        return math.pow(len(dividers)+1, 2)

    @classmethod
    def get_bucket_idx(cls, feature_value, field_name):
        bucket_idx = 0
        divider_lst = dividers[field_name]
        for divider in divider_lst:
            if feature_value < divider:
                break;
            bucket_idx += 1
        return bucket_idx
