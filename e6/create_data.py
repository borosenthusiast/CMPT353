import time
import numpy as np
import pandas as pd
from implementations import all_implementations
# ...

#data = pd.DataFrame(columns=['type', 'time'])

# for i in range(50):
#     random_array = np.arange(1, 30000)
#     np.random.shuffle(random_array)
#     for sort in all_implementations:
#         st = time.time()
#         res = sort(random_array)
#         en = time.time()
#         new_row = pd.Series({'type': sort.__name__, 'time': en-st})
#         data = data.append(new_row, ignore_index=True)

# data.to_csv('data.csv', index=False)

data = pd.DataFrame(columns=['qs1', 'qs2', 'qs3', 'qs4', 'qs5', 'merge1', 'partition_sort'])
totaltime = time.time()
for i in range(50):
    random_array = np.arange(1, 22000) #tuned to csil time
    np.random.shuffle(random_array)
    artime = []
    for sort in all_implementations:
        st = time.time()
        res = sort(random_array)
        en = time.time()
        artime.append(en-st)
    new_row = pd.Series({'qs1': artime[0], 'qs2': artime[1],'qs3': artime[2],'qs4': artime[3],'qs5': artime[4],'merge1': artime[5],'partition_sort': artime[6]})
    data = data.append(new_row, ignore_index=True)
endtime = time.time()

print("For 50 iterations of sorting 25000 elements, it took", endtime-totaltime, "seconds to complete.")
data.to_csv('data.csv', index=False)

# ~same time to execute