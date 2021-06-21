import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from skimage.color import lab2rgb
from skimage.color import rgb2lab
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
import sklearn.preprocessing
import sys


if len(sys.argv) >= 2:
    mdl = sys.argv[1]
    mdul = sys.argv[2]
    output = sys.argv[3]
else:
    mdl = 'monthly-data-labelled.csv'
    mdul = 'monthly-data-unlabelled.csv'
    output = 'labels.csv'

labelled = pd.read_csv(mdl)
unlabelled = pd.read_csv(mdul)

cities = labelled['city'].values
info = labelled.iloc[:,1:].values

#print(info)

X_train, X_valid, y_train, y_valid = train_test_split(info, cities)

model = make_pipeline(
    sklearn.preprocessing.StandardScaler(),
    KNeighborsClassifier(n_neighbors=6)
)
model.fit(X_train, y_train)

print(model.score(X_valid, y_valid))

ulinfo = unlabelled.iloc[:,1:].values
p = model.predict(ulinfo)

df = pd.DataFrame({'truth': y_valid, 'prediction': model.predict(X_valid)})
print(df[df['truth'] != df['prediction']])

#print(p)
pd.Series(p).to_csv(output, index=False, header=False)