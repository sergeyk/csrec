import cPickle
import numpy as np
import math
import csrec_paths
import pprint
import optparse


def generate_bucket_dividers(user_data_pkl_name='sampled_user_data.pkl',
                             divider_output_filename='bucket_dividers.pkl',
                             num_buckets=10):
    rows_lst = []
    print 'loading user data...'
    user_data = cPickle.load(open(csrec_paths.get_features_dir()+user_data_pkl_name, 'rb'))
    print 'data for %s users loaded' % (len(user_data))
    all_values = find_all_values_of_cols(user_data)
    bucket_dividers = {}
    for field_name, possible_values in all_values.iteritems():
        bucket_dividers[field_name] = get_dividers_from_values(possible_values, num_buckets)
    #pprint.pprint(bucket_dividers)
    cPickle.dump(bucket_dividers, open(csrec_paths.get_features_dir()+divider_output_filename, 'wb'))


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


def show_histogram(field_name = None,
                   user_data_pkl_name='sampled_user_data.pkl',
                   divider_output_filename='bucket_dividers.pkl',
                   num_buckets=10):
    rows_lst = []
    print 'loading user data...'
    user_data = cPickle.load(open(csrec_paths.get_features_dir()+user_data_pkl_name, 'rb'))
    print 'data for %s users loaded' % (len(user_data))
    all_values = find_all_values_of_cols(user_data)
    histograms = {}
    for field_name, possible_values in all_values.iteritems():
        histograms[field_name] = get_histograms_from_values(
            user_data[1346062][field_name]['field_type'],
            field_name, possible_values, num_buckets)
    #pprint.pprint(histograms)
    cPickle.dump(histograms, open(csrec_paths.get_features_dir()+divider_output_filename, 'wb'))


def get_histograms_from_values(field_type, field_name, possible_values, max_buckets):
    import matplotlib.pyplot as plt
    from numpy.random import normal
    gaussian_numbers = possible_values
    plt.hist(gaussian_numbers, bins=100)
    plt.title('%s (%s)' % (field_name, field_type))
    xlabel = "Value (%s unique)" % len(set(possible_values))
    plt.xlabel(xlabel)
    plt.ylabel("Frequency")
    plt.show()



if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option("-g", action="store", type="string", dest="field_name", 
                      help="show histogram for FIELD_NAME. Use '-g all' for all histograms.")
    parser.add_option("-d", action="store_true", dest="dividers", 
                      help="generate bin dividers")

    (options, args) = parser.parse_args()

    print options, args


    if options.dividers:
        generate_bucket_dividers()
    elif options.field_name:
        show_histogram(options.field_name)
    else:
        parser.print_help()
    #generate_bucket_dividers()
    #show_histogram()
