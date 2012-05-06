import cPickle
import numpy as np
import math
import csrec_paths
import pprint
import optparse
import feature_processor
import re
from collections import Counter

NUM_DIVIDERS = {'age': 5}
DEFAULT_NUM_DIVIDERS = 10
DIVIDERS = cPickle.load(open(csrec_paths.get_features_dir()+'bucket_dividers.pkl', 'rb'))
USER_DATA = None
ALL_VALUES = None
print DIVIDERS

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

def generate_bucket_dividers(user_data_pkl_name='sampled_user_data.pkl',
                             divider_output_filename='bucket_dividers.pkl'):
    ensure_user_data_loaded()
    bucket_dividers = {}
    for field_name, possible_values in ALL_VALUES.iteritems():
        if field_name in NUM_DIVIDERS:
            num_buckets = NUM_DIVIDERS[field_name]
        else:
            num_buckets= DEFAULT_NUM_DIVIDERS
        bucket_dividers[field_name] = get_dividers_from_values(possible_values, num_buckets)
    #pprint.pprint(bucket_dividers)
    cPickle.dump(bucket_dividers, open(csrec_paths.get_features_dir()+divider_output_filename, 'wb'))
    global DIVIDERS
    DIVIDERS = bucket_dividers


def get_dividers_from_values(possible_values, max_buckets):
    uniques = set(possible_values)
    num_unique = len(uniques)
    if num_unique < max_buckets:
        return sorted(list(uniques))
    else:
        sorted_values = sorted(possible_values)
        return sorted(list(set(sorted_values[0:-1:len(sorted_values)/max_buckets])))
        

def find_all_values_of_cols(user_data_dct):
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
        print 'number of unique values for', field_name, len(set(field_values))
    
    return all_values


def show_histogram(target_field_name = None,
                   user_data_pkl_name='sampled_user_data.pkl',
                   divider_output_filename='bucket_dividers.pkl',
                   num_buckets=10):
    ensure_user_data_loaded()
    histograms = {}
    if target_field_name.lower == 'all':
        for field_name, possible_values in ALL_VALUES.iteritems():
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


def find_top_x(field_name):
    ensure_user_data_loaded()
    possible_values = ALL_VALUES[field_name]
    c = Counter()
    for v in possible_values:
        c[v] += 1
    print c.most_common(10)
    ids = []
    for (c_id, cnt) in c.most_common(10):
        ids.append(int(c_id))
    print ids

if __name__ == "__main__":
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
        generate_bucket_dividers()
    elif options.field_name:
        generate_bucket_dividers()
        show_histogram(options.field_name)
    elif options.field_name_p:
        find_top_x(options.field_name_p)
    else:
        parser.print_help()
    
    #generate_bucket_dividers()
    #show_histogram()
