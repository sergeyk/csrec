#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb as mdb
import sys, os
import cPickle
import feature_contractor

def pickle_user_info(cursor):
    try:
        print 'loading data...'
        all_results = cPickle.load(open('db_query_results.pkl', 'rb'))
    except IOError:
        print 'querying database...'
        sql_cmd = "select * "+ \
            "from couchrequest as r inner join (user as us, user as uh) " + \
            "on (r.surf_user_id=us.user_id and r.host_user_id=uh.user_id) " + \
            "group by uh.user_id;"
        print sql_cmd
        cur.execute(sql_cmd)
        print 'finished query'
        all_results = cur.fetchall()
        cPickle.dump(all_results, open('db_query_results.pkl', 'wb'))
    print len(all_results)

    converter = feature_contractor.Converter()
    user_data = {}
    i = 0
    for result in all_results:
        i += 1
        print 'stored %s/%s' % (i, len(all_results))
        half = len(result)/2
        u1 = list(result[:half])
        u2 = list(result[half:])
        if u1[0] not in user_data:
            user_data[u1[0]] = converter.convert(u1)
        if u2[0] not in user_data:
            user_data[u2[0]] = converter.convert(u2)
    del(all_results)
    print 'dumping user data...'
    cPickle.dump(user_data, open('user_data.pkl', 'wb'))

con = None
username = os.environ['MYSQL_USER']
password = os.environ['MYSQL_PASS']

try:

    con = mdb.connect('localhost', username, 
        password, 'csrec');

    cur = con.cursor()
    pickle_user_info(cur)
        
except mdb.Error, e:
    print e
    sys.exit(1)
    
finally:    
        
    if con:    
        con.close()
