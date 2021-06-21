import numpy as np
import pandas as pd
import sys
import math
import matplotlib.pyplot as plt

#Haversine function adapted from exercise 3
def distance(city, stations):
    lat = city['latitude']
    lon = city['longitude']
    dlat = np.radians(np.subtract(stations['latitude'], lat))
    dlon = np.radians(np.subtract(stations['longitude'], lon))
    latr = math.radians(lat)
    lonr = math.radians(lon)
    a = np.power(np.sin(np.divide(dlat, 2)), 2) + math.cos(lat) * np.cos(np.radians(stations['latitude'])) * np.power(np.sin(np.divide(dlon, 2)), 2)
    c = np.multiply(2, np.arctan2(np.sqrt(a), np.sqrt(np.subtract(1, a))))
    return np.multiply(6371, c)

def best_tmax(city, stations):
    stations['distance'] = distance(city, stations)
    stations = stations[stations['distance'] == stations['distance'].min()].reset_index().loc[0, 'avg_tmax']
    return stations

if len(sys.argv) > 1:
    stations_file = sys.argv[1]
    city_data_file = sys.argv[2]
    output = sys.argv[3]
else:
    stations_file = 'stations.json.gz'
    city_data_file = 'city_data.csv'
    output = 'output.svg'

stations = pd.read_json(stations_file, lines=True)
stations['avg_tmax'] = stations['avg_tmax'].apply(lambda x: x / 10)
city_data = pd.read_csv(city_data_file)
city_data = city_data.dropna()
city_data['area'] = city_data['area'].apply(lambda x: x / 1000000)
city_data = city_data[city_data['area'] <= 10000]
city_data['avg_tmax'] = city_data.apply(best_tmax, axis=1, stations=stations)
city_data['population_density'] = city_data.apply(lambda x: x['population'] / x['area'], axis=1)

plt.scatter(city_data['avg_tmax'], city_data['population_density'])
plt.title('Temperature vs Population Density')
plt.xlabel('Avg Max Temperature (\u00b0C)')
plt.ylabel('Population Density (people/km\u00b2)')
plt.savefig(output)
plt.show()

#print(stations)
#print(city_data)