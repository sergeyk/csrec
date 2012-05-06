import cPickle
import csrec_paths
import math
import feature_processor
import numpy as np
from features.regions.region_id import *
from bucketizer import *

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
    
