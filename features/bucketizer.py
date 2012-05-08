import cPickle
import csrec_paths
import math
import feature_processor
import numpy as np
from features.regions.region_id import *
import test_bucketizer

# field-specific globals
INTEREST_BUCKETS = range(21)
BUCKETS_CONTINENT_ID = range(8)
BUCKETS_COUNTRY_ID = [244, 94, 84, 40, 190, 118, 271, 13, 216, 175]
BUCKETS_LANG = [163, 29, 35, 172, 39, 87, 162, 167, 155, 109]
cm = ContinentMapper()
CONVERTER  = feature_processor.Converter

class DefaultBucketizerFn(object):
    
    def pre_cross_dim(self, field_name):
        return (len(DEFAULT_DIVIDERS[field_name]) + 1)

    def post_full_dim(self, field_name):
        return self.post_cross_dim(field_name) +\
            2*self.pre_cross_dim(field_name)

    def post_cross_dim(self, field_name):
        return math.pow(self.pre_cross_dim(field_name), 2)

    def get_bucket_idx(self, field_name, feature_dct):
        feature_value = CONVERTER.convert(field_name, feature_dct)
        bucket_idx = 0
        dividers_lst = DEFAULT_DIVIDERS[field_name]
        for divider in dividers_lst:
            if feature_value <= divider:
                break;
            bucket_idx += 1
        return [bucket_idx]


class PopularBucketizerFn(DefaultBucketizerFn):
    
    def __init__(self, BUCKETS_LANG):
        self.mapping = {}
        for i in range(len(BUCKETS_LANG)):
           self.mapping[BUCKETS_LANG[i]] = i + 1
        self.num_buckets = len(self.mapping) + 1

    def get_popular_bucket_idx(self, value):
        if value:
            value = int(value)
        else:
            return 0
        if value in self.mapping:
            return self.mapping[value]
        else:
            return 0
        
    def get_bucket_idx(self, field_name, feature_dct):
        feature_value = CONVERTER.convert(field_name, feature_dct)
        val = self.get_popular_bucket_idx(feature_value)
        return [val]

    def pre_cross_dim(self, field_name):
        return self.num_buckets

class LangBucketizerFn(PopularBucketizerFn):

    def get_bucket_idx(self, field_name, feature_dct):
        languages = feature_dct['field_data']
        activated_bins = set([])
        for lang in languages:
            if lang[3] >= 2:
                activated_bins.add(self.get_popular_bucket_idx(lang[2]))
        return list(activated_bins)

class LocationsXBucketizerFn(PopularBucketizerFn):

    def get_bucket_idx(self, field_name, feature_dct):
        continents = feature_dct['field_data']
        activated_bins = set([])
        if not continents:
            return [0]
        if type(continents) == str:
            continents = [continents]
        for c in continents:
            activated_bins.add(self.get_popular_bucket_idx(cm.get_continent_id(c)))
        return list(activated_bins)

class InterestBucketizerFn(PopularBucketizerFn):
    
    def get_bucket_idx(self, field_name, feature_dct):
        bucketed = CONVERTER.convert(field_name, feature_dct)
        return bucketed
# globals
BUCKETIZER_FN_FOR_FIELD = {
    'profile': InterestBucketizerFn(INTEREST_BUCKETS),
    'languages': LangBucketizerFn(BUCKETS_LANG),
    'country_id': PopularBucketizerFn(BUCKETS_COUNTRY_ID),
    'locations_traveled': LocationsXBucketizerFn(BUCKETS_CONTINENT_ID),
    'locations_going': LocationsXBucketizerFn(BUCKETS_CONTINENT_ID),
    'locations_lived': LocationsXBucketizerFn(BUCKETS_CONTINENT_ID),
    'locations_desired': LocationsXBucketizerFn(BUCKETS_CONTINENT_ID)}

DEFAULT_BUCKETIZER_FN = DefaultBucketizerFn()

DEFAULT_DIVIDERS = cPickle.load(open(csrec_paths.get_features_dir()+'bucket_dividers.pkl', 'rb'))

def cross_bucketized_features(user1_dct, user2_dct, req_dct, 
                              feature_dimension, field_names, debug=True):
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
                crossed_idx_lst.append(crossed_index(bucketizer_fn.pre_cross_dim(field_name), 
                                                           bucket_idx1, bucket_idx2))
        offset_crossed_bucket_idx = cur_feature_offset
        offset_bucket_idx1 = offset_crossed_bucket_idx + \
            bucketizer_fn.post_cross_dim(field_name)
        offset_bucket_idx2 = offset_bucket_idx1 + \
            bucketizer_fn.pre_cross_dim(field_name)
                                             
        activated_idx_lst = []
        for bucket_idx1 in bucket_idx1_lst:
            activated_idx_lst.append(offset_bucket_idx1 + bucket_idx1)
        for bucket_idx2 in bucket_idx2_lst:
            activated_idx_lst.append(offset_bucket_idx2 + bucket_idx2)
        for crossed_idx in crossed_idx_lst:
            activated_idx_lst.append(offset_crossed_bucket_idx + crossed_idx)

        for activated_idx in activated_idx_lst:
            crossed_feature_vector[activated_idx] = 1
        
        cur_feature_offset += bucketizer_fn.post_full_dim(field_name)
    if debug:
        test_bucketizer.test(crossed_feature_vector, user1_dct, user2_dct, req_dct, 
                              feature_dimension, field_names)
    return crossed_feature_vector

def crossed_index(num_buckets, i1, i2):
    return i1*num_buckets+i2

def get_bucketizer_fn(field_name):
    if field_name in BUCKETIZER_FN_FOR_FIELD:
        return BUCKETIZER_FN_FOR_FIELD[field_name]
    else:
        return DEFAULT_BUCKETIZER_FN

def get_full_crossed_dimension(field_names_lst):
    dimension = 0
    for field_name in field_names_lst:
        fn = get_bucketizer_fn(field_name)
        dimension += fn.post_full_dim(field_name)
    return dimension
