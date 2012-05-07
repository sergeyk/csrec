#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb as mdb
import sys, os
import cPickle
import feature_processor
import csrec_paths
from MySQLdb import converters
import pprint
from cached_interests import cached_profiles
t = 0
c = 0
def get_languages(cursor, user_id):
    sql_cmd = "select * from %s where user_id=%s" % ('user_language', user_id)
    cursor.execute(sql_cmd)
    all_results = list(cursor.fetchall())
    return list(all_results)

def get_cached_profile(user_id):
    return cached_profiles[user_id]

def get_profile(cursor, user_id):
    global t,c
    t+=1
    if user_id in cached_profiles:
        c+=1
        print c,'/', t
        p_type = 'cached'
        data = get_cached_profile(user_id)
    else:
        p_type = 'db'
        data = get_db_profile(cursor, user_id)
    return {'field_type': p_type, 'field_data': data}

def get_db_profile(cursor, user_id):
    sql_cmd = "select * from %s where user_id=%s" % ('user_profile', user_id)
    cursor.execute(sql_cmd)
    
    all_results = list(cursor.fetchall())
    if len(all_results)>0:
        true_results = all_results[0]
        desc =  list(cursor.description)
        cols = [x[0] for x in desc]
    else:
        return {}
    output = {}
    for i in range(3,len(cols)):
        output[cols[i]] = true_results[i]
    return output

def pull_data_for_user(cursor, user_id):
    conv = converters.conversions
    user_data = {}
    tables = ['user', 'user_info']
    for table in tables:
        sql_cmd = "select * from %s where user_id=%s" % (table, user_id)
        cursor.execute(sql_cmd)
        all_results = list(cursor.fetchall())
        description = cursor.description
        for result in all_results:
            for i in range(len(result)):
                col_name = description[i][0]
                col_type = conv[description[i][1]]
                if col_name not in user_data:
                    new_field = {'field_type': col_type}
                    user_data[col_name] = new_field
                user_data[col_name]['field_data'] = result[i]
    user_data['languages'] = {'field_type': 'language_set',
                              'field_data': get_languages(cursor, user_id)}
    user_data['profile'] = get_profile(cursor, user_id)}
    return user_data
        

def pickle_competitor_set_user_info(cursor, competitor_set):
    active_user_ids = set([])
    sql_cmd = "select host_id, surfer_id from "+competitor_set
    cur.execute(sql_cmd)
    all_results = list(cur.fetchall())
    for result in all_results:
        active_user_ids.add(result[0])
        active_user_ids.add(result[1])
    print 'pulling data for', len(active_user_ids), 'users...'
    user_data_dct = {}
    i = 0
    for user_id in active_user_ids:
        i += 1
        user_data_dct[user_id] = pull_data_for_user(cursor, user_id)
        if i%1000 == 0:
            print "%s/%s" % (i, len(active_user_ids)), 'users finished'
            cPickle.dump(user_data_dct, 
                         open(csrec_paths.get_features_dir()+'sampled_user_data.pkl', 'wb'))

if __name__ == "__main__":
    con = None
    username = os.environ['MYSQL_USER']
    password = os.environ['MYSQL_PASS']

    try:
        
        con = mdb.connect('localhost', username, 
                          password, 'csrec');

        cur = con.cursor()
        pickle_competitor_set_user_info(cur, 'sample_competitor_sets')

    except mdb.Error, e:
        print e
        sys.exit(1)
    
    finally:    
        
        if con:    
            con.close()
