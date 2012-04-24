import _mysql as sql
import datetime
import Image, ImageDraw
import numpy as np
import sklearn.cluster
#from IPython import embed
import time
import cPickle
import os

class Sqler:
  def __init__(self):
    if os.path.exists('/u/vis/'):
      self.db = sql.connect(db='csrec',user='tobibaum',unix_socket='/u/vis/x1/sergeyk/mysql/mysql.sock')
    elif os.path.exists('/home/tobibaum/'):    
      self.db = sql.connect(db='CSRec')
    else:
      username = os.environ['MYSQL_USER']
      password = os.environ['MYSQL_PASS']
      self.db = sql.connect(db='csrec', user=username, passwd=password)

  def rqst(self, request, verbose=False):
    t = time.time()
    self.db.query(request)
    t -=time.time()
    
    if verbose:
      print 'db request took %f seconds'%(-t)
    res = self.db.use_result()
    self.res = res
    return res

  def get_row(self, style=1):
    return self.res.fetch_row(1,style)

  def get_top_host(self, table, top_k):
    res = self.rqst('SELECT host_user_id FROM ( SELECT host_user_id, \
    COUNT( * ) FROM ' + table + ' GROUP BY host_user_id ORDER BY 2 DESC  LIMIT '\
     + str(top_k) + ') AS T')
    top_hosts = [int(x['host_user_id']) for x in res.fetch_row(top_k, 1)]
    return top_hosts

  def get_hosts(self, table):
    res = self.rqst('select distinct host_user_id from ' + table)
    hosts = res.fetch_row(res.num_rows(),1)
    hosts = [int(h['host_user_id']) for h in hosts]
    return hosts
  
  def count_user_columns(self):
    res = self.rqst('SELECT * \
        FROM `user` \
        WHERE user_id =1')
    num = res.num_rows()
    rows = res.fetch_row(num,1)   
  
  def get_requests_for_host(self, host_id, table):
    res = self.rqst('SELECT * FROM (SELECT `date_arrival` , `date_departure` , \
      `rcd` , `rmd`  , `status` FROM '+table + 
      'WHERE `host_user_id` = ' + str(host_id) + ') as T ORDER BY `rmd`') 
    num = res.num_rows()
    rows = res.fetch_row(num,1)
    return rows
  
  def get_requests(self, table, lower, upper,machine):
    the_table = "(select couchrequest.host_user_id, couchrequest.status, \
    couchrequest.surf_user_id, couchrequest.id, couchrequest.rmd from couchrequest join \
    map_host_machine on (couchrequest.host_user_id = map_host_machine.host_user_id) \
    where map_host_machine.num = "+str(machine)+" ) as T"
    res = self.rqst("select host_user_id, status, surf_user_id, id, rmd from " + \
                    the_table+" order by host_user_id, rmd limit "+str(lower)+","+str(upper))
    # instead of all at a time fetch  the rows one after the other.
    return res # TODO: changing here!
  
    rows = []
    num_rows = res.num_rows()
    count = 0
    while True:
      print 'at row %d'%(count)
      count += 1
      row = res.fetch_row(1,0)      
      if row == ():
        break
      else: 
        row = row[0]
      rows.append(row)
      del row
    return rows

  def get_requests_for_host_just_june(self, host_id):
    res = self.rqst("SELECT * FROM ( SELECT `date_arrival` , `date_departure` ," +
                    " `rcd` , `rmd` , `status` FROM `couchrequest` WHERE `host_user_id` = " +
                    str(host_id) + " AND rmd < '2011-07-01 00:00:00' AND rmd > "+
                    "'2011-06-01 00:00:00') AS T ORDER BY `rmd` ") 
    num = res.num_rows()
    rows = res.fetch_row(num,1)
    return rows

  def get_max_depart(self, reqs):
    return np.max([self.convert_datetime(x['date_departure']) for x in reqs])
  
  def get_min_arrive(self, host_id, reqs):
    return np.min([self.convert_datetime(x['date_arrival']) for x in reqs])

  def get_min_request(self, host_id, reqs):
    return np.min([self.convert_datetime(x['rcd']) for x in reqs])

  def get_max_request(self, host_id, reqs):
    return np.max([self.convert_datetime(x['rcd']) for x in reqs])
    
  def convert_datetime(self, timestring):
    return datetime.datetime.strptime(timestring, '%Y-%m-%d %H:%M:%S')

 
  
