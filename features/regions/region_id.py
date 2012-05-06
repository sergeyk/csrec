'''
There is a 12-valued Region-ID in the 'user' table
'''
from competitor_sets.Sqler import Sqler
from countries import countries

import csrec_paths
import numpy as np
from numpy import *
import cPickle
import os

class ContinentMapper:
  def __init__(self):
    self.map = cPickle.load(open(os.path.join(csrec_paths.ROOT,'features','regions','country_map_continent.pkl'),'r'))
    self.continents = ['', 'Africa', 'Antarctica', 'Asia', 'Europe', 'North America',
                       'Oceania', 'South America']

  def get_continent_id(self, country):
    return self.continents.index(self.get_continent_name(country))

  def get_continent_name(self, country):
    if not self.map.has_key(country):
      return ''
    else:
      return self.map[country]
  
def print_continentmap(cont_map):
  print 'continents: '
  
  for ind, cont in enumerate(cont_map):
    print '%d - %s...'%(ind, cont)
  print '\n'

def create_continent_map():
  cm = ContinentMapper()
  if not os.path.exists('locations_list'):#cs_counts'):
    sq = Sqler()
    res = sq.rqst("SELECT country, region_id from `user`")
    full_map = sq.get_all_rows(0)
    arr = np.array(full_map)
    cs_counts = np.unique(arr[:,0])
    cPickle.dump(cs_counts, open('cs_counts', 'w'))
  else:
    cs_counts = cPickle.load(open('locations_list'))#'cs_counts', 'r'))
  #their_map = {x['name']:x['continent'] for x in countries}
  their_map = cPickle.load(open('their_map', 'r'))    
  map = {}
  
#  for count in their_map:
#    country = count['country']
#    if country in cs_counts:
#      map[country] = count['continent']
    #  for each country find a match in
  their_countrys = map.keys()
  cPickle.dump(map, open('map', 'w'))
  our_countries = cPickle.load(open('country_map_continent.pkl','r'))
  our_countries = our_countries.keys() 
  
  not_mapped=[]
  for c in cs_counts: 
    if not c in our_countries:
      not_mapped.append(str(c))
  cont_map = cm.continents
  print_continentmap(cont_map)
  
  counter = 0
  new_mapped = {}
  for nm in not_mapped:
    counter += 1
    if counter > 5:
      print_continentmap(cont_map)
      counter = 0
          
    selection = raw_input(nm)
    new_mapped[nm] = str(cont_map[int(selection)])
    
  map.update(new_mapped)
  cPickle.dump(map, open('full_map','w'))  
  
def run():
  create_continent_map()
  cm = ContinentMapper()
  print cm.get_continent_name('Germany')
  print cm.get_continent_id('France')
  
if __name__=='__main__':
  run()
  