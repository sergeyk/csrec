import os

ROOT = os.path.dirname(os.path.abspath(__file__))

def get_dataset_dir():
    return ROOT+'/datasets'

def get_proj_root():
    return ROOT
