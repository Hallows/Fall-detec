import numpy as np
from sklearn import svm
from sklearn.externals import joblib

# Generate train data
X = np.loadtxt('norXY')
print(X)

ax='0.035,'
ay='0.618,'
ax=float(ax[:-1])
ay=float(ay[:-1])
print("x->%f y->%f"%(ax,ay))
nninput=np.array([ax,ay])
nninput=np.reshape(nninput,(-1,2))
print(nninput)
