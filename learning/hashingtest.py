# -*- coding: utf-8 -*-
"""
Created on Mon Apr 23 18:25:38 2012

@author: Tim
"""

#!/bin/env python

import matplotlib.pyplot as plt
import numpy as np
import time


def hash1(x,y,N): # obv. bad
    return x+y%N

# some ideas from:
    
def hash2(x,y,N):
    return ((x * 0x1f1f1f1f) ^ y)%N

def hash3(x,y,N):
    a = ((y & 0xffff) << 16) | (x & 0xffff)
    a = (a ^ 61) ^ (a >> 16)
    a = a + (a << 3)
    a = a ^ (a >> 4)
    a = a * 0x27d4eb2d
    a = a ^ (a >> 15)
    return a%N
    
def hash4(x,y,N): #bad
    return ((y & 0xffff) << 16) | (x & 0xffff)%N
    
def hash5(x,y,N): # take this one
    a = (x * 0x1f1f1f1f) ^ y
    a = (a ^ 61) ^ (a >> 16)
    a = a + (a << 3)
    a = a ^ (a >> 4)
    a = a * 0x27d4eb2d
    a = a ^ (a >> 15)
    return a%N  
    
hashsize = 10 # size in MB
N = hashsize * 1000000 / 8 # assuming 64bit floats 

hashfunction = hash5
#N = 1<<32
nhosts = 1000
nfeatures = 10000

nbins = 1000

t0 = time.time()
hashvalues = []
for host in xrange(nhosts):
    print "host", host
    for feature in xrange(nfeatures):
        hashvalues.append(hashfunction(host,feature,N))
t1 = time.time()

plt.hist(hashvalues, bins=np.linspace(0, N, nbins, endpoint=True), normed=True)
plt.title("Histogram over hashvalues")
plt.xlabel("Value")
plt.ylabel("Frequency")
plt.show()

print "took time:", t1-t0 # hash2 60sec, hash3 115sec, hash5 125sec
print N 
print nhosts * nfeatures

## compute number of collisions
#n1 = len(hashvalues)
#s = set(hashvalues)
#n2 = len(s)
#ncollisions = n1 - n2
#print "ncollisions", ncollisions
#print "collisionrate", ncollisions / float(n1)
#print "avg. collision per hashvalue", ncollisions/float(N)
#print "avg. optimal spread out would be", n1/float(N)

            