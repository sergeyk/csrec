#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb as mdb
import sys, os
import cPickle
import feature_contractor

def pickle_sample_user_info(cursor):
    print 'loading sampled user data...'
    user_data = cPickle.load(open('user_data.pkl', 'rb'))
    print 'querying database...'
    sql_cmd = "select host_id,  surfer_id "+ \
        "from competitor_sets"
    print sql_cmd
    cur.execute(sql_cmd)
    print 'finished query'
    all_results = cur.fetchall()
    id_set = set([])
    for result in all_results:
        for i in result:
            id_set.add(i)
    sampled_user_data = {}
    not_found_ids = set([])
    for user_id in id_set:
        if user_id in user_data:
            sampled_user_data[user_id] = user_data[user_id]
        else:
            not_found_ids.add(user_id)
    print not_found_ids
    #print sampled_user_data
    print 'dumping...'
    cPickle.dump(sampled_user_data, open('sampled_user_data.pkl', 'wb'))

def pickle_user_info(cursor):
    try:
        print 'loading data...'    
        all_results = cPickle.load(open('db_query_results.pkl', 'rb'))
    except IOError:
        print 'querying database 1...'
        sql_cmd = "select u.* "+ \
            "from couchrequest as r inner join (user as u) " + \
            "on (r.surf_user_id=u.user_id) group by u.user_id;"
        print sql_cmd
        cur.execute(sql_cmd)
        print 'finished query 1'
        all_results = list(cur.fetchall())
        print 'querying database 2...'
        sql_cmd = "select u.* "+ \
            "from couchrequest as r inner join (user as u) " + \
            "on (r.host_user_id=u.user_id) group by u.user_id;"
        print sql_cmd
        cur.execute(sql_cmd)
        print 'finished query 2'
        all_results += list(cur.fetchall())
        cPickle.dump(all_results, open('db_query_results.pkl', 'wb'))
    print len(all_results)

    converter = feature_contractor.Converter()
    user_data = {}
    i = 0
    for result in all_results:
        i += 1
        print 'stored %s/%s' % (i, len(all_results))
        u1 = list(result)
        if u1[0] not in user_data:
            user_data[u1[0]] = converter.convert(u1)
    del(all_results)
    print len(user_data), 'users loaded'
    print 'dumping user data...'
    cPickle.dump(user_data, open('user_data.pkl', 'wb'))

con = None
username = os.environ['MYSQL_USER']
password = os.environ['MYSQL_PASS']

try:

    con = mdb.connect('localhost', username, 
        password, 'csrec');

    cur = con.cursor()
    print len(sys.argv)
    if len(sys.argv) == 1:
        pickle_user_info(cur)
    else:    
        pickle_sample_user_info(cur)

except mdb.Error, e:
    print e
    sys.exit(1)
    
finally:    
        
    if con:    
        con.close()
