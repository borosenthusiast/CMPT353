import sys
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats
import statsmodels.api as sm
from pykalman import KalmanFilter

def to_timestamp(d):
    return datetime.timestamp(d)


csvfile = sys.argv[1]
#csvfile = "sysinfo.csv" #Testing code
cpuinfo = pd.read_csv(csvfile, parse_dates=[0])
#cpuinfo['time'] = cpuinfo['timestamp'].apply(to_timestamp)
#print(cpuinfo)
lowess_smoothed = sm.nonparametric.lowess(cpuinfo['temperature'], cpuinfo['timestamp'], frac=0.02)

kalman_data = cpuinfo[['temperature', 'cpu_percent', 'sys_load_1', 'fan_rpm']]

initial_state = kalman_data.iloc[0]
observation_covariance = np.diag([0.9,5,0.9,200]) ** 2
transition_covariance = np.diag([0.01,0.01,0.01,0.01]) ** 2
transition = [[0.97,0.5,0.2,-0.001],[0.1,0.4,2.2,0],[0,0,0.95,0],[0,0,0,0]]
kf = KalmanFilter(initial_state_mean=initial_state, initial_state_covariance=observation_covariance,observation_covariance=observation_covariance
    ,transition_covariance= transition_covariance, transition_matrices=transition)
kalman_smoothed, _ = kf.smooth(kalman_data)

plt.figure(figsize=(12,4))
plt.plot(cpuinfo['timestamp'], cpuinfo['temperature'], 'b.', alpha=0.5, label='CPU Temperature Data')
plt.plot(cpuinfo['timestamp'], kalman_smoothed[:, 0], 'g-')
plt.plot(cpuinfo['timestamp'], lowess_smoothed[:, 1], 'r-')
plt.legend(['CPU Temperature Data', 'Kalman Smoothing', 'LOWESS Smoothing'])
plt.xlabel('Timestamp')
plt.ylabel('CPU Temperature')
#plt.show()
plt.savefig('cpu.svg')

#plt.figure(figsize=(12,4))
#plt.plot(cpuinfo['timestamp'], cpuinfo['temperature'], 'b.', alpha=0.5)
#plt.show()