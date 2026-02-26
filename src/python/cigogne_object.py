#!/usr/bin/env python3

"""
Read and extract data from the ciconia database
"""

from shapely.geometry import Point, Polygon

import matplotlib.pylab as plt
import numpy as np
from operator import itemgetter

class ciconia(object):
  def __init__(self, filename="0000635-251009101135966.csv", path="../data/cigogne"):
    """
    self.db : array of [lat, lon, day, month, year] for each observation
    """
    self.path     = path
    self.filename = '%s/%s'%(path, filename)
    self.db       = []

    self.read_db()

  # --------------------------------------------------------------------------------------------------------
  def read_db(self):
    db = []
    fic=open(self.filename, encoding="utf8")
    line = fic.readline() # read header
    try:
      while True:
        line = fic.readline()
        if not(len(line)):
          raise EOFError
        try: # if the day if not filled, put 1:
          day   = int(float(line.split('\t')[30]))
        except ValueError:
          day   = 1
        try:
          lat   = float(line.split('\t')[21])
          lon   = float(line.split('\t')[22])
          month = int(float(line.split('\t')[31]))
          year  = int(float(line.split('\t')[32]))
          db.append([lat, lon, day, month, year])
        except ValueError: # data not filled in database
          pass
    except EOFError:
      fic.close()

    self.db = np.array(db)

  # --------------------------------------------------------------------------------------------------------
  def select_area(self, coord, dist, dist_unit='degree', overwrite=False, select=False):
    """
    Select the data in a square of given center (lat/lon) and distance (in km).

    dist_unit : 'km', 'degree'
    overwrite : True/False - overwrite self.db with this selection ?
    select    : True/False - overwrite self.db_select with this selection ? 
    """
    x = coord[0]
    y = coord[1]

    if dist_unit == 'km':
      # Convert 'km' into 'degree'
      dist = dist/111.19 # 1 degree ~= 111 km

    polygon = Polygon([[x-dist,y-dist], [x+dist,y-dist], [x+dist,y+dist], [x-dist,y+dist]])

    db_select = []
    for k in range(len(self.db)):
      point = Point(self.db[k,0], self.db[k,1])
      if point.within(polygon):
        db_select.append(self.db[k,:])

    if overwrite:
      self.db = np.array(db_select)
    elif select:
      self.db_select = np.array(db_select)
    else:
      return np.array(db_select)

  # --------------------------------------------------------------------------------------------------------
  def getFirstInRegion(self, NperDay=1):
    """
    Search for the date of observation of the first bird in the selected area for each year.

    NdayObs : minimum number of observation per day to consider the day as the date of first observation

    return : dict[year] = [day,month]
    """
    from collections import OrderedDict

    first = {}
    try:
      for year in set(self.db_select[:,-1]):
        m = np.array([row[2:4] for row in self.db_select if int(row[-1]) == int(year)])
        if NperDay == 1:
          first[int(year)] = list(map(int,sorted(m, key=lambda x: (x[1], x[0]))[0]))
        else: # Only take the first day where there is at least NperDay observation :
          counts = OrderedDict()
          for x in sorted(m, key=lambda x: (x[1], x[0])):
            key = tuple(x)   # arrays are not hashable, tuples are
            counts[key] = counts.get(key, 0) + 1

            if counts[key] >= NperDay:
              first[int(year)] = [int(key[0]), int(key[1])]
              break
      return first
    except IndexError: # No observation
      return None

  # --------------------------------------------------------------------------------------------------------
  def save_db(self, filename="cigogne_db_Alsace.dat"):
    """
    Save the database into a file
    """
    fic = open('%s/%s'%(self.path,filename), 'wt')
    for k in range(len(self.db)):
      fic.write("%10.6f %10.6f %2d %2d %4d\n"%(self.db[k,0], self.db[k,1], self.db[k,2], self.db[k,3], self.db[k,4]))
    fic.close()

# ==========================================================================================================
def seen_before(center, around):
  """
  Compare the two dictionaries and returns if a bird have been seen around before in the center 

  return dict[year] = True/False
  """
  output = {}
  for year in center.keys():
    output[year] = 0
    if around[year][1]<center[year][1] or (around[year][1]==center[year][1] and around[year][0]<center[year][0]):
      output[year] = 1
  return output
