from nlp.extraction import interest_extractor

#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb as mdb
import sys, os
import cPickle

def pickle_user_info(cursor):
    user_data = {}
        #"us.description, us.interests, us.music_movies_books, us.people_i_enjoy, " + \
        #"uh.description, uh.interests, uh.music_movies_books, uh.people_i_enjoy " + \
    sql_cmd = "select * "+ \
        "from couchrequest as r inner join (user as us, user as uh) " + \
        "on (r.surf_user_id=us.user_id and r.host_user_id=uh.user_id) " + \
        "where r.status='Y' " + \
        "group by uh.user_id;"

    cur.execute(sql_cmd)
    all_results = cur.fetchall()
    i = 0
    for results in all_results:
        i += 1
        print 'stored %s/%s' % (i, len(all_results))
        half = len(results)/2
        u1 = list(results[:half])
        u2 = list(results[half:])
        if u1[0] not in user_data:
            user_data[u1[0]] = u1
        if u2[0] not in user_data:
            user_data[u2[0]] = u2
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
