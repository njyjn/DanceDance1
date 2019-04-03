import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import confusion_matrix
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import RandomizedSearchCV
from sklearn.externals import joblib


PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
data_processed_path = os.path.join(PROJECT_DIR, 'sklearn', 'processed-pre-midterm')
features = pd.read_csv(os.path.join(data_processed_path, 'dataFeatures.csv'))
print('The shape of our features is:', features.shape)

# Labels are the values we want to predict
labels = np.array(features['dance'])

# Remove the labels from the features
# axis 1 refers to the columns
features = features.drop('dance', axis = 1)

# Saving feature names for later use
feature_list = list(features.columns)

# Convert to numpy array
features = np.array(features)

# Split the data into training and testing sets
train_features, test_features, train_labels, test_labels = train_test_split(features, labels, test_size= 0.25, random_state = 42)

# Instantiate model with 5 neighbours
knn = KNeighborsClassifier(n_neighbors=5)

# Train the model on training data
knn.fit(train_features, train_labels)

from sklearn.model_selection import cross_val_score, KFold
import numpy as np
#create a new KNN model
knn_cv = KNeighborsClassifier(n_neighbors=5)
#train model with cv of 5
cv_scores = cross_val_score(knn_cv, train_features, train_labels, cv=KFold(n_splits=5))
#print each cv score (accuracy) and average them
# print(cv_scores)
print('cv_scores mean:{}'.format(np.mean(cv_scores)*100)+'%')

model_path = os.path.join(PROJECT_DIR, 'models', 'kNN.pkl')
print("Saving model.")
joblib.dump(knn, model_path)
print("Model successfully saved at %s" % model_path)