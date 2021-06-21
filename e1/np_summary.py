import numpy as np

data = np.load('monthdata.npz')
#Each column in a month Jan-Dec of a particular year
totals = data['totals'] #total precipitation in a year, jan-dec
counts = data['counts'] #number of oberservations recorded in a given month

# #print(totals)
# print(counts)

# 1) Which city had the lowest total precipitation over the year?
sumtotal = np.sum(totals, axis=1)
#print(sumtotal)
minimum = np.argmin(sumtotal)
print("Row with lowest total precipitation:\n", minimum)


# 2) Determine the average precipitation in these locations for each month
avg = np.divide(np.sum(totals, axis=0), np.sum(counts, axis=0))
print("Average precipitation in each month:")
print(avg)

# # 3) Average precipitation for each city
avg = np.divide(np.sum(totals, axis=1), np.sum(counts, axis=1))
print("Average precipitation in each city:")
print(avg)

# # 4) Calculate the total precipitation for each quarter in each city
totals_reshape_size = int((totals.size / 12) * 4)
#print(totals_reshape_size)
quarterly_totals = np.reshape(np.sum(np.reshape(np.ravel(totals), (totals_reshape_size,3)), axis=1), (int(totals_reshape_size / 4), 4))
print("Quarterly precipitation totals")
print(quarterly_totals)
