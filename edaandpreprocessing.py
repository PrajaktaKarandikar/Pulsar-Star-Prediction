# -*- coding: utf-8 -*-
"""EDAandPreprocessing

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Jj3MpjOxO6z9-VeQHkDi3wxNL9vAvdUD
"""

from google.colab import drive
drive.mount('/content/drive')

import os
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import train_test_split
from sklearn.feature_selection import RFE
from collections import Counter
from scipy.io import arff

#import utils
#import modules

import warnings
warnings.filterwarnings("ignore")
#set seed
np.random.seed(30)
sns.set_style("darkgrid")

PROJ_DIR = '//'.join(os.path.dirname("/content/drive/MyDrive/EE660_Proj/").split("/"))
DATA_DIR = '//'.join(os.path.dirname("/content/drive/MyDrive/EE660_Proj/Data").split("/"))

#Read data from local directory
df = arff.loadarff("/content/drive/MyDrive/HTRU_2.arff")
data = pd.DataFrame(df[0])
print("Shape:", data.shape)

#Split data into train, validation and test sets
X = data.iloc[:,0:8]
y = data.iloc[:, -1]
X_train, X_test, y_train,  y_test = train_test_split(X, y, test_size=0.20, random_state=30)
X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=0.20, random_state=30)

print(X_train.shape, X_test.shape, X_val.shape, y_test.shape)

#check data head to take a look
print('Data head:', X_train.head())
#describe the data 
print(X_train.describe(include='all'))
#check for categorical values
print(X_train.dtypes)
#check for missing values
print(X_train.isnull().sum())

# Get the class distribution
labels = y_train.iloc[:]
counter = Counter(labels)
for a, b in counter.items():
  perct = b / len(labels) * 100
  print('Class=%s, Count=%d, Percentage=%.2f%%' % (a, b, perct))     

# Visualizing the distribution of each class
plt.figure(figsize = (10, 8))
total = float(len(X_train))
ax = sns.countplot(x = y_train, data = X_train)
ax.set_title("Data Distribution Per Class")
for d in ax.patches:
  height = d.get_height()
  ax.text((d.get_x()+d.get_width()/2.0), height + 3, '{:1.2f}'.format(height/total), ha="center") 
plt.savefig(os.path.join(PROJ_DIR, "ClassDistribution_Plot.png"), bbox_inches="tight", dpi=200)
plt.show()

#Plot histograms for data exploration
D_train=X_train.copy()
for features in list(X_train.columns[:]):
  fig, axes = plt.subplots(figsize=(8, 4))
  sns.histplot(x=D_train[features].dropna(), bins=42)
  plt.grid(True)
  fig.savefig(os.path.join(PROJ_DIR, "Histogram_Plots_{}.png".format(features)), bbox_inches="tight", dpi=200)
plt.show()

#Check for outliers

for i in range(len(X_train.columns[:])):
  features = X_train.columns[:]
  plt.figure(figsize = (8, 5))
  sns.boxplot(x = y_train, y =  (list(X_train.columns[:]))[i], data = X_train)
  plt.grid(True)
  plt.savefig(os.path.join(PROJ_DIR, "Box_Plots_{}.png".format(i)), bbox_inches="tight", dpi=200)
plt.show()

#Correlation check
plt.figure(figsize = (8, 8))
corr_mat = X_train.corr()
sns.heatmap(corr_mat, xticklabels = corr_mat.columns, yticklabels = corr_mat.columns, annot=True, fmt=".2f", linecolor="blue")
plt.title("Correlation HeatMap")
plt.savefig(os.path.join(PROJ_DIR, "Correlation_Map.png"), bbox_inches="tight", dpi=200)
plt.show()

#Encode labels
for i in range(len(y_train)):
  if y_train.iloc[i] == "b'0'":
    y_train.iloc[i] = 0
  elif y_train.iloc[i] == "b'1'":
    y_train.iloc[i] = 1
y_train = y_train.astype(int)
#validation data
for i in range(len(y_val)):
  if y_val.iloc[i] == "b'0'":
    y_val.iloc[i] = 0
  elif y_val.iloc[i] == "b'1'":
    y_val.iloc[i] = 1
y_val = y_val.astype(int)
#test data
for i in range(len(y_test)):
  if y_test.iloc[i] == "b'0'":
    y_test.iloc[i] = 0
  elif y_test.iloc[i] == "b'1'":
    y_test.iloc[i] = 1
y_test = y_test.astype(int)

y_train = y_train.to_frame(name = 'class')
y_val = y_val.to_frame(name = 'class')
y_test = y_test.to_frame(name = 'class')

#Handle Class Imbalance
sm = SMOTE(sampling_strategy=1,random_state = 30)
X_tr_bal, y_tr_bal = sm.fit_resample(X_train, y_train)
X_train = pd.DataFrame(X_tr_bal, columns = data.iloc[:, 0:8].columns)
y_train = pd.DataFrame(y_tr_bal, columns=['class'])

X_test.shape

y_train = y_train.set_index(X_train.index)
train1 = X_train.join(y_train)

y_val = y_val.set_index(X_val.index)   
val1 = X_val.join( y_val)

y_test = y_test.set_index(X_test.index)
test1 = X_test.join(y_test)

#Remove outliers
Q1 = train1.quantile(0.25)
Q3 = train1.quantile(0.75)
IQR = Q3 - Q1
lower_range= Q1 - (1.5 * IQR)
upper_range= Q3 + (1.5 * IQR)
num_outliers = ((train1 < (lower_range)) | (train1 > (upper_range))).sum()
print('Number of Outliers Present:'), '%', '\n'
print(num_outliers)

num_outliers.to_csv (os.path.join(PROJ_DIR, 'NumOuliers.txt'), index = False, header=True)
train1 = train1[~((train1< (Q1 - 1.5 * IQR)) |(train1 > (Q3 + 1.5 * IQR))).any(axis=1)]

#Get the splits again
X_train = train1.iloc[:, 0:8]
y_train = train1.iloc[:, -1].to_frame(name = 'class')

X_val = val1.iloc[:, 0:8]
y_val = val1.iloc[:, -1].to_frame(name = 'class')

X_test = test1.iloc[:, 0:8]
y_test = test1.iloc[:, -1].to_frame(name = 'class')

#Standardize the data
Scaler = StandardScaler()
Scaler.fit(X_train)
X_train = pd.DataFrame(Scaler.transform(X_train), columns=train1.iloc[:, 0:8].columns.values.tolist())
X_val = pd.DataFrame(Scaler.transform(X_val), columns=train1.iloc[:, 0:8].columns.values.tolist())
X_test = pd.DataFrame(Scaler.transform(X_test), columns=train1.iloc[:, 0:8].columns.values.tolist())

#Create files to save preprocessed data for  later use.
#save training data
y_train = y_train.set_index(X_train.index)
train2 = X_train.join(y_train)
train2.to_csv (os.path.join(DATA_DIR, "training_data.csv"), index = False, header=True)
# save validation data  
y_val = y_val.set_index(X_val.index)   
val2 = X_val.join( y_val)
val2.to_csv (os.path.join(DATA_DIR, "validation_data.csv"), index = False, header=True)
#save test data 
y_test = y_test.set_index(X_test.index)
test2 = X_test.join(y_test)
test2.to_csv (os.path.join(DATA_DIR, "test_data.csv"), index = False, header=True)