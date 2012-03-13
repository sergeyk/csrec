#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb as mdb
import sys, os


def print_num_hosts(cursor):
    cur.execute("SELECT count(*) FROM user WHERE user.couch_available='Y';")
    print 'num_hosts', int(cur.fetchone()[0])

def print_num_surfers(cursor):
    cur.execute("SELECT count(*) FROM (SELECT user_id, count(*) as times_hosted FROM user JOIN couchrequest ON (user.user_id=couchrequest.surf_user_id) GROUP BY user_id)sub;")
    print 'num_surfers', int(cur.fetchone()[0])

def print_req_per_host(cursor):
    counts = {}
    cur.execute('SELECT * FROM (SELECT user_id, count(*) as times_hosted FROM user JOIN couchrequest ON (user.user_id=couchrequest.host_user_id) GROUP BY user_id)sub;')
    for tup in cur.fetchall():
        val = int(tup[1])
        if val in counts:
            counts[val] += 1
        else:
            counts[val] = 1
    print counts
    import matplotlib.pyplot as plt
    X = []
    Y = []
    for x, y in counts.iteritems():
        X.append(x)
        Y.append(y)
    print X
    print Y
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    ax.set_xscale('log')
    plt.plot(X,Y, 'ro')
    plt.ylabel('# Users')
    plt.xlabel('Total # requests received')
    plt.show()

con = None
username = os.environ['MYSQL_USER']
password = os.environ['MYSQL_PASS']

try:

    con = mdb.connect('localhost', username, 
        password, 'csrec');

    cur = con.cursor()
    print_num_hosts(cur)
    print_num_surfers(cur)
    print_req_per_host(cur)
        
except mdb.Error, e:
  
    print "Error %d: %s" % (e.args[0],e.args[1])
    sys.exit(1)
    
finally:    
        
    if con:    
        con.close()
