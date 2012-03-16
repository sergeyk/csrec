#!/usr/bin/python
from biz.business_logic import BusinessLogic as bl
import os, sys, inspect
from math import sqrt
from optparse import OptionParser
from biz import global_db
from parsing import parseNetflix
import util as ut
import update_functions as uf


OPTIONS = None
DB_NAME = 'db'
DATA_DIR = '/knn_test_data'

def make_prediction(u, i):
    knn = bl.get_rated_knn(u, i)
    normalization = 1.0/sqrt(len(knn))
    g_avg = bl.get_global_avg()
    b_u = bl.get_user_bias(u)
    b_i = bl.get_item_bias(i)
    total = 0.0

    for j in knn:
        weight = bl.get_weight(i, j)
        r_uj = bl.get_rating(u,j)
        b_j = bl.get_item_bias(j)
        b_uj = g_avg + b_u + b_j

        total += (r_uj - b_uj) * weight

    return g_avg + b_u + b_i + normalization * total


def update_parameters():    
    usr_id_list = bl.get_all_user_ids()
    
    for usr_id in usr_id_list:
        rated_items = bl.get_items_rated_by_user(usr_id) #remember to add
        for itm_id in rated_items:
            r_ui = make_prediction(usr_id,itm_id)
            rating = bl.get_rating(usr_id,itm_id)
            e_ui = rating - r_ui
            uf.update_user_bias(usr_id, e_ui)
            uf.update_item_bias(itm_id, e_ui)
            uf.update_weights(usr_id, itm_id, e_ui)
            

def find_global_avg():
    usr_list = bl.get_all_user_ids()
    itm_list = bl.get_all_item_ids() #fix
    total = 0.0
    num_ratings = 0
    
    for usr_id in usr_list:
        rated_items = bl.get_items_rated_by_user(usr_id)

        for itm_id in rated_items:
            num_ratings += 1
            total += bl.get_rating(usr_id, itm_id)

    g_avg = total/ num_ratings
    bl.set_global_avg(g_avg)
    

def init_db_for_learning():
    bl.set_lambda(2, 0)
    bl.set_learning_rate(.0005)
    bl.set_lambda(4, .002)
    
    find_global_avg()
    ut.compute_and_set_items_knn(\
            ut.shrunk_pearson_correlation, 5)
    for user_id in bl.get_all_user_ids():
        bl.set_user_bias(user_id, 0)
    for item_id in bl.get_all_item_ids():
        bl.set_item_bias(item_id, 0)
        knn = bl.get_item_knn(item_id)
        for neighbor in knn:
            bl.set_weight(item_id, neighbor, 0)
            

def main():
    if not global_db.db_initialized(os.getcwd()+'/'+ DB_NAME):
        global_db.create_new_netflix_db(DB_NAME)
        parseNetflix.parse_netflix_data(DATA_DIR)
    else:
        global_db.set_db(DB_NAME)
    init_db_for_learning()
    for i in range(OPTIONS.iterations):
        update_parameters()
    global_db.shutdown_db()


if __name__ == '__main__':
    global OPTIONS
    parser = OptionParser()
    parser.add_option("-i", "--iterations",
                      action="store", type="int", dest="iterations")
    (OPTIONS, args) = parser.parse_args()
    
    if OPTIONS.iterations:
        main()
