import cPickle
import csrec_paths
import math
import feature_processor
import numpy as np
from features.regions.region_id import *

# field-specific globals
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


# globals
BUCKETIZER_FN_FOR_FIELD = {'languages': LangBucketizerFn(BUCKETS_LANG),
                           'country_id': PopularBucketizerFn(BUCKETS_COUNTRY_ID),
                           'locations_traveled': LocationsXBucketizerFn(BUCKETS_CONTINENT_ID),
                           'locations_going': LocationsXBucketizerFn(BUCKETS_CONTINENT_ID),
                           'locations_lived': LocationsXBucketizerFn(BUCKETS_CONTINENT_ID),
                           'locations_desired': LocationsXBucketizerFn(BUCKETS_CONTINENT_ID)}

DEFAULT_BUCKETIZER_FN = DefaultBucketizerFn()

DEFAULT_DIVIDERS = cPickle.load(open(csrec_paths.get_features_dir()+'bucket_dividers.pkl', 'rb'))

def cross_bucketized_features(user1_dct, user2_dct, req_dct, 
                              feature_dimension, field_names):
    cur_feature_offset = 0
    crossed_feature_vector = np.zeros(feature_dimension, np.dtype(np.int32))

    for field_name in field_names:
        bucketizer_fn = get_bucketizer_fn(field_name)
        bucket_idx1_lst = bucketizer_fn.get_bucket_idx(field_name,
                                                   user1_dct[field_name])
        bucket_idx2_lst = bucketizer_fn.get_bucket_idx(field_name,
                                                   user2_dct[field_name])
        offset_crossed_bucket_idx = cur_feature_offset
        offset_bucket_idx1 = offset_crossed_bucket_idx + \
            bucketizer_fn.post_cross_dim(field_name)
        offset_bucket_idx2 = offset_bucket_idx1 + \
            bucketizer_fn.pre_cross_dim(field_name)
        
        activated_idx_lst = []
        for bucket_idx1 in bucket_idx1_lst:
            for bucket_idx2 in bucket_idx2_lst:
                activated_idx_lst.append(offset_crossed_bucket_idx + \
                                             crossed_index(bucketizer_fn.pre_cross_dim(field_name), 
                                                           bucket_idx1, bucket_idx2))
        for bucket_idx1 in bucket_idx1_lst:
            activated_idx_lst.append(offset_bucket_idx1 + bucket_idx1)
        for bucket_idx2 in bucket_idx2_lst:
            activated_idx_lst.append(offset_bucket_idx2 + bucket_idx2)

        for activated_idx in activated_idx_lst:
            crossed_feature_vector[activated_idx] = 1
            
        cur_feature_offset += bucketizer_fn.post_full_dim(field_name)

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

######### HISTOGRAM SHIT BELOW ############

NUM_DIVIDERS = {'age': 5}
DEFAULT_NUM_DIVIDERS = 10
DIVIDERS = cPickle.load(open(csrec_paths.get_features_dir()+'bucket_dividers.pkl', 'rb'))
USER_DATA = None
ALL_VALUES = None


def find_all_values_of_cols(user_data_dct):
    all_values = {}
    i = 0
    for user_id, data_dct in user_data_dct.iteritems():
        i += 1
        for field_name, field_dct in data_dct.iteritems():
            if field_name not in all_values:
                all_values[field_name] = []
            bucketizer_fn = get_bucketizer_fn(field_name)
            bucket_idx1_lst = bucketizer_fn.get_bucket_idx(field_name,
                                                           data_dct[field_name])
            all_values[field_name] += bucket_idx1_lst
        if i%1000 == 0:
            print "%s/%s" % (i, len(user_data_dct)), 'users finished'
       
    for field_name, field_values in all_values.iteritems():
        print 'number of unique values for', field_name, len(set(field_values))
    
    return all_values


def ensure_user_data_loaded():
    user_data_pkl_name='sampled_user_data.pkl'
    global USER_DATA, ALL_VALUES
    if not USER_DATA:
        print 'loading user data...'
        USER_DATA = cPickle.load(open(csrec_paths.get_features_dir()+user_data_pkl_name, 'rb'))
        #pprint.pprint(USER_DATA[1346062]['languages'])
        #raise

        print 'data for %s users loaded' % (len(USER_DATA))
        ALL_VALUES = find_all_values_of_cols(USER_DATA)


def show_histogram(target_field_name = None,
                   user_data_pkl_name='sampled_user_data.pkl',
                   divider_output_filename='bucket_dividers.pkl',
                   num_buckets=10):
    import re
    f = open(csrec_paths.get_features_dir()+'relevant_features', 'rb')
    field_names = []
    if f:
        for line in f:
            line = re.sub(r'\s', '', line)
            if len(line)>1:
                field_names.append(line)
    ensure_user_data_loaded()
    histograms = {}
    if target_field_name.lower() == 'all':
        for field_name, possible_values in ALL_VALUES.iteritems():
            if field_name in field_names:
                histograms[field_name] = get_histograms_from_values(
                    USER_DATA[1346062][field_name]['field_type'],
                    field_name, possible_values, num_buckets)
    else:
        possible_values = ALL_VALUES[target_field_name]
        get_histograms_from_values(
            USER_DATA[1346062][target_field_name]['field_type'],
            target_field_name, possible_values, num_buckets)


def get_histograms_from_values(field_type, field_name, possible_values, max_buckets):
    import matplotlib.pyplot as plt
    from numpy.random import normal
    gaussian_numbers = possible_values
    plt.hist(gaussian_numbers, bins=100)
    plt.title('%s (%s)' % (field_name, field_type))
    xlabel = "Value (%s unique) %s" % (len(set(possible_values)), DIVIDERS[field_name])
    plt.xlabel(xlabel)
    plt.ylabel("Frequency")
    plt.show()


if __name__ == "__main__":
    import optparse
    parser = optparse.OptionParser()
    parser.add_option("-g", action="store", type="string", dest="field_name", 
                      help="show histogram for FIELD_NAME. Use '-g all' for all histograms.")
    parser.add_option("-d", action="store_true", dest="dividers", 
                      help="generate bin dividers")
    parser.add_option("-p", action="store", type="string", dest="field_name_p", 
                      help="show histogram for FIELD_NAME. Use '-g all' for all histograms.")
    (options, args) = parser.parse_args()

    print options, args


    if options.dividers:
        pass
    elif options.field_name:
        show_histogram(options.field_name)
    elif options.field_name_p:
        pass
    else:
        parser.print_help()
    
