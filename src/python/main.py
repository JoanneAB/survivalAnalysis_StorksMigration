#!/usr/bin/env python3

"""
Read and extract data from the ciconia database
"""

from shapely.geometry import Point, Polygon

import matplotlib.pylab as plt
import numpy as np
from operator import itemgetter
import datetime

from cigogne_object import ciconia, seen_before
from weather_moon import get_weather, isWeatherWarmBefore, get_moonIllumination

# ==========================================================================================================
# ==========================================================================================================
if __name__=='__main__':

  NperDay = 1 # Number of ciconia observation per day to select the day as the day of first observation 
  warmTemperature = 8

  # --------------------------------------------------------------------------------------------------------
  # --------------------------------------------------------------------------------------------------------
  fic_csv = open('../database_%dperDay_isWarm%d_new.csv'%(NperDay, warmTemperature), 'wt')
  fic_csv.write('id,start,stop,event,isWarm,latitude,longitude,temperature,windSpeed,pressure,humidity,visibility,nebulosity,cloudHeight,moonPhase\n')

  # --------------------------------------------------------------------------------------------------------
  # --------------------------------------------------------------------------------------------------------
  cigogne = ciconia(filename="0000635-251009101135966_small.csv")

  # Only keep a small dataset arount Alsace to reduce the working dataset.
  # for now, only in Alsace because handling weather add more complexities but possible in the future...
  cigogne.select_area(coord=[48.30197, 7.581915], dist=1, overwrite=True)

  # --------------------------------------------------------------------------------------------------------
  # --------------------------------------------------------------------------------------------------------
  idi = 0
  dist  = 0.08 # distance in degrees to form the square of observation arount coord
  for lat in np.linspace(47.5, 49.0, 10):
    for lon in np.linspace(6.95, 8.15, 8):
      coord = [lat, lon] # Point of interest
      # ---- Get first observation in user-defined area
      # Get the subset area as defined by the user:
      cigogne.select_area(coord=coord, dist=dist, select=True)

      # Get day/month of the first observation in the region for each year:
      first_select = cigogne.getFirstInRegion(NperDay)

      if first_select: # If observation
        for year in first_select.keys():
          idi = idi + 1
          day, month = first_select[year] 
          try:
            # Get the weather:
            temperature, windSpeed, pressure, humidity, visibility, nebulosity, cloudHeight = get_weather(coord[0], year, month, day)
        
            # Get to know if warm days during at least four consecutive days before observation:
            isWarm, warm2obs = isWeatherWarmBefore(coord[0], year, month, day, warmTemperature)

            # Get the fraction of the moon illuminated:
            moon = get_moonIllumination(year, month, day)
            
            days2obs = datetime.datetime(year, month, day).timetuple().tm_yday
            if isinstance(warm2obs, int):
              # One line for time-0 to end time of 4-consecutive days of warm (no cicona yet):
              days2warm = days2obs - warm2obs
 
              # Get the weather and moon at time of obs:
              newDate = datetime.date(year, 1, 1) + datetime.timedelta(days=days2warm - 1)
              newT, newWS, newP, newH, newV, newN, newCH = get_weather(coord[0], newDate.year, newDate.month, newDate.day)
              newM = get_moonIllumination(newDate.year, newDate.month, newDate.day)
              csv2write = '%3d,%3d,%3d,0,1,%5.2f,%4.2f,%4.1f,%4.1f,%8.1f,%5.1f,%7.1f,%5.1f,%6.1f,%5.1f\n'%(idi, 0, days2warm, coord[0],coord[1], newT, newWS, newP, newH, newV, newN, newCH, newM)
              csv2write = csv2write.replace('-9999.0','')
              fic_csv.write(csv2write)

              # One second line from days2warm to days2obs :
              csv2write = '%3d,%3d,%3d,1,1,%5.2f,%4.2f,%4.1f,%4.1f,%8.1f,%5.1f,%7.1f,%5.1f,%6.1f,%5.1f\n'%(idi, days2warm, days2obs,coord[0],coord[1],temperature, windSpeed, pressure, humidity, visibility, nebulosity, cloudHeight, moon)
              csv2write = csv2write.replace('-9999.0','')
              fic_csv.write(csv2write)
            else:
              # One line from time-0 to days2obs:
              csv2write = '%3d,%3d,%3d,1,0,%5.2f,%4.2f,%4.1f,%4.1f,%8.1f,%5.1f,%7.1f,%5.1f,%6.1f,%5.1f\n'%(idi, 0, days2obs,coord[0],coord[1],temperature, windSpeed, pressure, humidity, visibility, nebulosity, cloudHeight, moon)
              
              csv2write = csv2write.replace('-9999.0','')
              fic_csv.write(csv2write)

          except TypeError:
            pass # no data for this year. Before 1994
  
  fic_csv.close()
