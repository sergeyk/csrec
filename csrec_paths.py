import os

ROOT = os.path.dirname(os.path.abspath(__file__))

def get_config_dir():
    return ROOT + '/train_test/config/'

def get_dataset_dir():
    return ROOT + '/datasets/'

def get_features_dir():
    return ROOT + '/features/'

def get_proj_root():
    return ROOT
