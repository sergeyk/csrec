import _mysql as sql
import datetime
import numpy as np
import sklearn.cluster
from IPython import embed
import time
import cPickle
import os
from Sqler import *
from mpi4py import MPI
import shutil
import csrec_paths

comm = MPI.COMM_WORLD
comm_rank = comm.Get_rank()
comm_size = comm.Get_size()
 
def swap_inds(arr, a, b):
  arr[np.where(arr==a)[0]] = -1
  arr[np.where(arr==b)[0]] = a
  arr[np.where(arr==-1)[0]] = b

def rename_clusters(cluster):
  smallest_ind = 0
  last_ind = -1
  for idx in range(cluster.shape[0]):
    index = cluster[idx]
    if not index == last_ind:
      if index < smallest_ind:
        embed()
        #raise RuntimeError("Well...What? they should be ordered!")
      # swap vals
      swap_inds(cluster, smallest_ind, index)
      last_ind = smallest_ind
      smallest_ind+=1      

def split_requests(reqs, cluster):
  req_sets = []
  req_set = []
  curr_cl = cluster[0] 
  
  for idx, req in enumerate(reqs):
    cl = cluster[idx]
    if cl == curr_cl:
      req_set.append(req)
    else:
      req_sets.append(req_set)
      req_set = [req]
      curr_cl = cl
      
  req_sets.append(req_set)
  return req_sets
  
def clusterize(sq, reqs):
  # ========= Cluster Responses =============
  rsps_raw = [sq.convert_datetime(x[4]) for x in reqs]
  
  min_rsp = np.min(rsps_raw)
  rsps = [int((x-min_rsp).total_seconds()) for x in rsps_raw]
  rsps_arr = np.asmatrix(rsps).T
  max_rsp = np.max(rsps_arr)
  if max_rsp == 0:
    return [reqs]
  rsps_arr = rsps_arr/float(max_rsp)
  ms = sklearn.cluster.mean_shift(np.asarray(rsps_arr), 60*30/float(max_rsp))
  
  cluster = ms[1]
  rename_clusters(cluster)
  
  # Get reqest sets
  req_sets = split_requests(reqs, cluster)
  
  try:
    assert (len(reqs) == sum(len(x) for x in req_sets))
  except:
    embed()
  return req_sets  

def get_sessions(lower, upper, force=False):
  sq = Sqler()
  table = 'couchrequest'  
  
  filename = 'cluss_'+str(comm_rank)
  if os.path.exists(filename) and not force:
    return
  
  t = time.time() 
  res = sq.get_requests(table,lower,upper)
  t -= time.time()
  print 'db query took %f sec'%(-t)  
      
  last_hid = -1
  reqs = [] 
  rows = res.fetch_row(11000000,0)
  print 'read all rows'
  num_rows = len(rows)
  print 'there are %d rows'%num_rows

  cluss = []
  for rowdex in range(num_rows):
    row = rows[rowdex]
    
    hid = row[0]
    if not last_hid == hid and not last_hid == -1:
      # we have a new host
      print 'at host %s'%last_hid
      into_next = False
      if len(reqs) == 0:
        reqs.append(row)
      else:
        into_next = True    
      clus = clusterize(sq, reqs)      
      cluss += clus                              
      reqs = [row]      
    else:
      reqs.append(row)    
    last_hid = hid  
  cPickle.dump(cluss, open(filename,'w'))


def create_sessions():  
  num_hosts = 845024
  upper = num_hosts/comm_size
  lower = comm_rank*upper
  if comm_rank == comm_size - 1:
    # This is the last machine, why don't we just give it the remaining hosts.
    upper*=2  
  print '%d: %d - %d'%(comm_rank, lower,upper)
  get_sessions(lower, upper, force=False)
  
def new_filehandle(i):
  filename = 'insert_file_%d.sql'%i
  shutil.copyfile('fill_comp_set_blank', filename)
  file_out = open(filename, 'a')
  return file_out

def compile_sessions():
  fileextension = 0
  file_out = new_filehandle(fileextension)    
  very_first = True  
  comp_set_id = 0
  too_much_count = 0
  
  for i in range(2):
    read_cluss = cPickle.load(open('cluss_%d'%i,'r'))
    print 'opened file %d'%i
    ###################
    for cl in read_cluss:        
      for r in cl:
        if not very_first:
          file_out.writelines(',\n')
        else:
          very_first=False  
        winner = (r[1] == 'Y')
        # in-order: host_user_id, status, surf_user_id, id, rmd
        # out-order: req_id, set_id, host_id, surfer_id, winner, date
        write_string = "( "+str(r[3])+" , "+ str(comp_set_id)+" , "+str(r[0]) + \
          " , "+ str(r[2])+" , "+str(int(winner))+ " , '"+str(r[4])+ "' )"
        file_out.writelines(write_string)
      
      print 'wrote comp set %d'%comp_set_id
      too_much_count += 1
      if too_much_count > 300000:
        fileextension += 1
        too_much_count = 0
        file_out.close()
        file_out = new_filehandle(fileextension)
      comp_set_id += 1        
    ###################
  file_out.writelines(';')  
  
if __name__=='__main__':
  if comm_size > 1:
    create_sessions()
  else:
    compile_sessions()