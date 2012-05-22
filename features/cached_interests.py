import csrec_paths
import cPickle

pkl_path = csrec_paths.get_features_dir()+'interests/interest_extraction/merged_interest_dct.pkl'
cached_profiles_dct = cPickle.load(open(pkl_path,'rb'))
