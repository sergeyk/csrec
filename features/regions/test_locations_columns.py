import csrec_paths
import numpy as np
from numpy import *
from features.regions.region_id import ContinentMapper
from competitor_sets.Sqler import Sqler
import cPickle
import os

try:
  from IPython import embed
except:
  print 'embed not available'

def run():
  sq = Sqler()
  cm = ContinentMapper()
  cm.get_continent_name('Germany')
  
  filename = 'locations_list'
  if not os.path.exists(filename):
    request = "SELECT locations_traveled, locations_desired, locations_lived, \
      locations_going FROM `user_info`"
    
    print 'fetching all location columns...'
    sq.rqst(request, verbose=True)
    rows = sq.get_all_rows(0, True)
    s = set()
    for rowdex, row in enumerate(rows):
      print 'at row %d'%rowdex    
      full_row = row[0]+','+row[1]+','+row[2]+','+row[3]
      countries = np.array(np.unique(full_row.split(',')), dtype='str').tolist()
      for x in countries:
        s.add(str(x).strip())
    cPickle.dump(list(s), open(filename, 'w'))
  else:
    l = cPickle.load(open(filename, 'r'))
    
  missing_countries = []
  cm = ContinentMapper()
  
  stored_countries = cm.map.keys()
  for country in l:
    if not country in stored_countries:
      missing_countries.append(country)
  
  new_map = {}
  their_map = cPickle.load(open('their_map', 'r'))
  #  embed()
  for country in their_map:
    continent = their_map[country]
    if country in missing_countries:
      new_map[country] = continent
  embed()  

if __name__=='__main__':
  run()