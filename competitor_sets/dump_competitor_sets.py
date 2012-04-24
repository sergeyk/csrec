import _mysql as sql
import datetime
import Image, ImageDraw
import numpy as np
import sklearn.cluster
from IPython import embed
import time
import cPickle
import os
from Sqler import *
from mpi4py import MPI
comm = MPI.COMM_WORLD
comm_rank = comm.Get_rank()
comm_size = comm.Get_size()



def plot_host(sq, reqs, cluster):
  # ========= PLOT THIS HOST ================
  x_off = 20
  y_off = 20
  width = 1040
  height = 680
  w = width - x_off
  h = height - y_off
  
  im = Image.new("RGB",(width, height), 'white')
  draw = ImageDraw.Draw(im)

  draw.line((x_off, y_off) + (x_off, height), fill=128)
  draw.line((x_off, y_off) + (width, y_off), fill=128)
  
  max_dep = sq.get_max_depart(reqs)
  min_arr = sq.get_min_arrive(reqs)  
  delta_period = (max_dep - min_arr).total_seconds()
  
  min_req = sq.get_min_request(reqs)
  max_req = sq.get_max_request(reqs)
  delta_req = (max_req - min_req).total_seconds()

  red_rects = []
  red_lines = []
  rsp_duration = []
  
  last_cluster = -1
  
  start_point = (sq.convert_datetime(reqs[0]['rmd']) - min_req).total_seconds()-60
  
  colors = [(0,1,0), (1,0,0), (0,0,1)]

  for rq_idx, req in enumerate(reqs):
    arrival = (sq.convert_datetime(req['date_arrival']) - min_arr).total_seconds()/delta_period
    depart = (sq.convert_datetime(req['date_departure']) - min_arr).total_seconds()/delta_period
    req_time = (sq.convert_datetime(req['rcd']) - min_req).total_seconds()
    rsp_time_x = (sq.convert_datetime(req['rmd']) - min_arr).total_seconds()
    rsp_time_y = (sq.convert_datetime(req['rmd']) - min_req).total_seconds()
    rsp_duration.append(rsp_time_y - req_time)
    rect = [x_off + w* arrival, y_off + req_time/delta_req*h-5, x_off + w*depart, y_off + req_time/delta_req*h+5]
    rect2 = [x_off-5, y_off + rsp_time_y/delta_req*h-1, x_off+5, y_off + rsp_time_y/delta_req*h+1]
    rect3 = [y_off + rsp_time_x/delta_period*w-1,x_off-5, y_off + rsp_time_x/delta_period*w+1,  x_off+5]
    
    accepted = req['status']
    if accepted == 'Y':
      red_rects.append(rect)
      red_rects.append(rect2)
      red_rects.append(rect3)
      red_lines.append(((rect2[2], rect2[1]+1), (rect[0],rect[1]+3)))
      #red_lines.append(((rect3[2]-1, rect3[1]+1), (rect[0],rect[1]+3)))
    
    else:
      draw.rectangle(rect, fill='#B1B1B1', outline='black')
      draw.rectangle(rect2, fill='#B1B1B1', outline='black')
      draw.rectangle(rect3, fill='#B1B1B1', outline='black')
      color = colors[cluster[rq_idx]%3]
      draw.line((rect2[2], rect2[1]+1) + (rect[0],rect[1]+3), fill=color)
      #draw.line((rect3[2], rect3[1]+1) + (rect[0],rect[1]+3), fill=256)
    
    cluster_ind = cluster[rq_idx]
    if not cluster_ind == last_cluster:
      # we found a new cluster. draw a vertical line from last point to here.
      end_point = rsp_time_y + 60
      draw.line((x_off/2,y_off + start_point/delta_req*h)+(x_off/2,y_off + end_point/delta_req*h), fill=256)
       
      last_cluster = cluster_ind      
      if rq_idx+1< len(reqs):
        start_point = (sq.convert_datetime(reqs[rq_idx+1]['rmd']) - min_req).total_seconds()-60    
      
  #print len(red_rects)  
  for rect in red_rects:
    draw.rectangle(rect, fill='#FF0000', outline='black')

  for line in red_lines:
    draw.line(line[0] + line[1], fill=255)
      
  im.show()
  #im.save('late_response_guy.png')
  del im
  del draw 
  
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
        raise RuntimeError("Well...What? they should be ordered!")
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
  return req_sets
  
def clusterize(sq, reqs):
  # TODO: This can definitely be sped up!
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

  return req_sets  

def get_sessions(suffix,lower,upper,force=False, machine=0):
  sq = Sqler()
  sq_write = Sqler()
#  sq.count_user_columns()
#  table = 't_good_hosts_2010_requests'
  table = 'couchrequest'  
  
  filename = 'all_requests_'+suffix+'_'+str(machine)
  if os.path.isfile(filename) and not force:
    all_rqsts = cPickle.load(open(filename, 'r'))
    print 'load db from file'
  else:
    t = time.time() 
    res = sq.get_requests(table,lower,upper,machine)
    t -= time.time()
    print 'db query took %f sec'%(-t)
    cPickle.dump(all_rqsts, open(filename, 'w'))
      
  # format all_rqsts: host_user_id, status, surf_user_id, id, rmd
  #num_rows = len(all_rqsts)
  last_hid = -1
  reqs = []
  comp_set_id = 0
  t = time.time()
#  suitor_sets = []
  while True:
    row = res.fetch_row(1,0)      
    if row == ():
      break
    else: 
      row = row[0]      
    #row = all_rqsts[rowdex]
    
    hid = row[0]
    if not last_hid == hid and not last_hid == -1:
      # we have a new host
      print 'at host %s'%last_hid
      # do something with reqs
      into_next = False
      if len(reqs) == 0:
        reqs.append(row)
      else:
        into_next = True  
    
      t_clus = time.time()
      clus = clusterize(sq_write, reqs)
      t_clus -= time.time()
      
      curr_rqst = "INSERT INTO `competitor_sets` VALUES"
      for cl in clus:        
        for r in cl:
          winner = (r[1] == 'Y')
          curr_rqst += "( "+str(r[3])+" , "+ str(comp_set_id)+" , "+str(last_hid) + \
            " , "+ str(r[2])+" , "+str(int(winner))+ " , '"+str(r[4])+ "' ),"
        #print "r", curr_rqst
        comp_set_id += 1
      sq_write.rqst(curr_rqst[:-1]+";")
        
            
#      print '\tclus: %f'%(-t_clus)      
#      
#      t_add_reqs = time.time()
#      for idx, cl in enumerate(clus):
#        winner = None
##        suitor_set = {'hostID':int(last_hid)}
#        surfs = []
#        try:
#          for r in cl:
#            if r[1] == 'Y':
#              #host_user_id, status, surf_user_id, id, rmd
#              winner = int(r[2])
#            surfs.append((int(r[2]), int(r[3])))
#        except:
#          embed()
##        suitor_set['list_surfers'] = surfs
##        suitor_set['winner'] = winner 
#        suitor_set2 = (int(last_hid), surfs, winner)
##        suitor_sets.append(suitor_set)
#        suitor_sets2.append(suitor_set2)
#      t_add_reqs -= time.time()
#      print '\tadd: %f'%(-t_add_reqs)
      if into_next:
        reqs = [row]
      else:
        reqs = []
    else:
      reqs.append(row)
    
    last_hid = hid
  t -= time.time()
  print 'that all took %f sec'%(-t)
  
  #embed()
#  cPickle.dump(suitor_sets, open('suitor_sets_'+suffix,'w'))
  #cPickle.dump(suitor_sets2, open('suitor_sets_tuple_'+suffix,'w'))
  print 'finished'
  return  
  

if __name__=='__main__':
  
#  lower = 5464099
#  upper = 2*lower+1
  lower = 0
  #upper = 5464099
  upper = 10000
  
  
  suffix = 'train'#'train_'+str(lower)+'_'+str(upper)
  get_sessions(suffix, lower, upper, force=True, machine=comm_rank)
  #get_sessions('test', 5464099, 5464100)