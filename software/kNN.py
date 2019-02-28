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

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
data_processed_path = os.path.join(PROJECT_DIR, 'dance-dance-software', 'HAPT Data Set', 'processed')
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

# min_max_scaler = MinMaxScaler()
# np_scaled = min_max_scaler.fit_transform(features)
# normalized = pd.DataFrame(np_scaled)
# normalized.columns = feature_list
# normalized.head()

# Split the data into training and testing sets
train_features, test_features, train_labels, test_labels = train_test_split(features, labels, test_size= 0.25, random_state = 42)

# print('Training Features Shape:', train_features.shape)
# print('Training Labels Shape:', train_labels.shape)
# print('Testing Features Shape:', test_features.shape)
# print('Testing Labels Shape:', test_labels.shape)

# Mean Normalization to have a faster classifier
sc = StandardScaler()
X_train_array = sc.fit_transform(train_features)

# Assign the scaled data to a DataFrame & use the index and columns arguments to keep your original indices and column names:
train_features = pd.DataFrame(X_train_array)
X_test_array = sc.transform(test_features)
test_features = pd.DataFrame(X_test_array)

# Instantiate model with 5 neighbours
knn = KNeighborsClassifier(n_neighbors=5)

# Train the model on training data
knn.fit(train_features, train_labels)

# Use predict method on the test data
predictions = knn.predict(test_features)

# Calculate the absolute errors
errors = abs(predictions - test_labels)

# Calculate mean absolute percentage error (MAPE)
mape = 100 * (errors / (test_labels+1))

# Calculate and display accuracy
accuracy = 100 - np.mean(mape)
print('Accuracy:', accuracy, '%.')

# Print out confusion matrix
conf_mat = confusion_matrix(test_labels, predictions)
print(conf_mat)

###################################################################################################################

# from sklearn.model_selection import cross_val_score
# import numpy as np
# #create a new KNN model
# knn_cv = KNeighborsClassifier(n_neighbors=5)
# #train model with cv of 5
# cv_scores = cross_val_score(knn_cv, train_features, train_labels, cv=5)
# #print each cv score (accuracy) and average them
# print(cv_scores)
# print('cv_scores mean:{}'.format(np.mean(cv_scores)))
#
# from sklearn.model_selection import GridSearchCV
# #create new a knn model
# knn2 = KNeighborsClassifier()
# #create a dictionary of all values we want to test for n_neighbors
# param_grid = {'n_neighbors': np.arange(1, 25)}
# #use gridsearch to test all values for n_neighbors
# knn_gscv = GridSearchCV(knn2, param_grid, cv=5)
# #fit model to data
# knn_gscv.fit(test_features, test_labels)
# print(knn_gscv.best_params_)
# print(knn_gscv.best_score_)
