import sys
import pandas as pd
import matplotlib.pyplot as plt

filename1 = sys.argv[1]
filename2 = sys.argv[2]

d1 = pd.read_csv(filename1, sep=' ', header=None, index_col=1, names=['lang', 'page', 'views', 'bytes'])
d2 = pd.read_csv(filename2, sep=' ', header=None, index_col=1, names=['lang', 'page', 'views', 'bytes'])

d1 = d1.sort_values(['views'], ascending=False)
#print(d1)

d1['views_after'] = d2['views']
#print(d1)

plt.figure(figsize=(10,5))

plt.subplot(1,2,1)
plt.plot(d1['views'].values)
plt.xlabel('Rank')
plt.ylabel('Views')
plt.title('Popularity Distribution')

plt.subplot(1,2,2)
plt.scatter(d1['views'], d1['views_after'])
plt.title('Daily Correlation')
plt.xlabel('Day 1 Views')
plt.ylabel('Day 2 Views')
plt.xscale('log')
plt.yscale('log')

plt.savefig('wikipedia.png')