import sys
import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
import scipy.stats as stats
from statsmodels.stats.multicomp import pairwise_tukeyhsd

data = pd.read_csv('data.csv')
print(data)
anova = stats.f_oneway(data['qs1'], data['qs2'], data['qs3'], data['qs4'], data['qs5'], data['merge1'], data['partition_sort'])

print(anova)
print(anova.pvalue)


#Using example from slides, stats tests
x_melt = pd.melt(data)
x_melt['value'] = x_melt['value']

posthoc = pairwise_tukeyhsd(
    x_melt['value'], x_melt['variable'],
    alpha=0.05)

print(posthoc)

fig = posthoc.plot_simultaneous()
plt.show()