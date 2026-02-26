#!/usr/bin/env python3

"""
Read and extract data from the weather and moon illumation database
"""

from shapely.geometry import Point, Polygon
import os
import numpy as np

# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
def get_line_weather(lat, year, month, day, time="12:00", path="..\\data\\weather"):
  """
  Returns the corresponding line of data for the latitude and year/month/day
  """
  filename = '%s\\synop_%d.csv'%(path, year)

  # Choose which station to get data from
  if lat > 48.3:
    station = "STRASBOURG-ENTZHEIM"
  else:
    station = "BALE-MULHOUSE"

  # Exact time of observation not known, take 12:00 or 15:00 if 12:00 missing
  # FIXME get hour too ?
  if os.path.exists(filename):
    try:
      output = os.popen("FINDSTR %s %s | FINDSTR %4d-%02d-%02dT%s"%(station, filename, year, month, day, time)).read().split(';')
    except EOFError:
      output = os.popen("FINDSTR %s %s | FINDSTR %4d-%02d-%02dT15:00"%(station, filename, year, month, day)).read().split(';')

    if len(output)>13:
      return output
    else: 
      return None
  else:
    return None

# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
def get_weather(lat, year, month, day, path="..\\data\\weather"):
  """
  Get the weather parameters for each bird observation
  """
  output = get_line_weather(lat, year, month, day)

  if output: 
    temperature = float(output[13]) - 273.15 # Kelvin -> Celsius
    try:
      windSpeed   = float(output[12]) # m/s
    except ValueError:
      windSpeed = -9999
    try:
      pressure    = float(output[26]) # Pa
    except ValueError:
      pressure = -9999
    try:
      humidity    = float(output[15]) # %
    except ValueError:
      humidity    = -9999
    try:
      visibility = float(output[16]) # m ; horizontal visibility
    except ValueError:
      visibility = -9999
    try:
      nebulosity = float(output[20]) # %
    except ValueError:
      nebulosity = -9999
    try:
      cloudHeight = float(output[22]) # m ; height of the lower layer of clouds
    except ValueError:
      cloudHeight = -9999

    return([temperature, windSpeed, pressure, humidity, visibility, nebulosity, cloudHeight])
  else:
    return None 

# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
def isWeatherWarmBefore(lat, year, month, day, warmTemperature=8, path="..\\data\\weather"):
  """
  Return True/False if there were at least four consecutive days before year/month/day 
  where the temperature at 6am was greater than 8 degrees.
  """
  import datetime
  
  line = get_line_weather(lat, year, month, day, time='06:00')

  timeDelta = datetime.timedelta(days=1)
  obsDay = datetime.datetime(year, month, day)

  temperatures = [[obsDay, float(line[13])-273.15]]
  Nobs = 0

  while Nobs <= 30: # Check only in the last 30 days
    Nobs = Nobs+1
    # Look at previous day:
    obsDay = obsDay - timeDelta

    try:
      temperature = float(get_line_weather(lat, obsDay.year, obsDay.month, obsDay.day, time='06:00')[13]) - 273.15
      if temperature >= warmTemperature:
        # Compute the number of days between this date and the last entry:
        diff = (temperatures[-1][0] - obsDay).days
        # Save the data:
        temperatures.append([obsDay, diff, temperature])
        try:
          # If there are four consecutive days:
          if temperatures[-1][1] + temperatures[-2][1] + temperatures[-3][1] == 3:
            return 1, (temperatures[0][0] - temperatures[-3][0]).days
        except IndexError: # not enough data to check yet.
          pass
    except (TypeError, ValueError):
      pass
  return 0, "NA"

# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
def get_moonIllumination(year, month, day, path="..\\data\\moon"):
  """
  Get the fraction of the moon illumination (in percent) for each bird observation
  """
  filename = '%s\\%4d'%(path, year)

  try:
    fic = open(filename, 'rt')
    fic.readline() # read header
    for _ in range(day):
      line = fic.readline()
    fic.close()

    return 100*float(line.split()[int(month)+1])
  except:
    return -9999

