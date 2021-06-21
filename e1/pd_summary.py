import pandas as pd

totals = pd.read_csv('totals.csv').set_index(keys=['name'])
counts = pd.read_csv('counts.csv').set_index(keys=['name'])

#print(totals)
#print(counts)

#1 Which city had the lowest total precipitation over the year?
minimum = totals.sum(axis=1).idxmin()
print("City with the lowest precipitation:")
print(minimum)

#2 Determine the average precipitation in these locations for each month.
average_city_precipitation = totals.sum(axis=0).div(counts.sum(axis=0))
print("Average precipitation in each month:")
print(average_city_precipitation)

#3 Average precipitation for each city
average_city_precipitation = totals.sum(axis=1).div(counts.sum(axis=1))
print("Average precipitation in each city:")
print(average_city_precipitation)