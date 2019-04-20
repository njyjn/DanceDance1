import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix
import os
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
train_features, test_features, train_labels, test_labels = train_test_split(features, labels, test_size = 0.25, random_state = 42)

# Instantiate model with 1000 decision trees
rf = RandomForestClassifier(n_estimators = 1000, random_state = 42)

# Train the model on training data
rf.fit(train_features, train_labels)

# Use the forest's predict method on the test data
predictions = rf.predict(test_features)

# Calculate the absolute errors
errors = abs(predictions - test_labels)

# Calculate mean absolute percentage error (MAPE)
mape = 100 * (errors / (test_labels))

# Calculate and display accuracy
accuracy = 100 - np.mean(mape)
print('Accuracy:', accuracy, '%.')

# Number of trees in random forest
n_estimators = [int(x) for x in np.linspace(start = 200, stop = 2000, num = 10)]
# Number of features to consider at every split
max_features = ['auto', 'sqrt']
# Maximum number of levels in tree
max_depth = [int(x) for x in np.linspace(10, 110, num = 11)]
max_depth.append(None)
# Minimum number of samples required to split a node
min_samples_split = [2, 5, 10]
# Minimum number of samples required at each leaf node
min_samples_leaf = [1, 2, 4]
# Method of selecting samples for training each tree
bootstrap = [True, False]
# Create the random grid
random_grid = {'n_estimators': n_estimators,
               'max_features': max_features,
               'max_depth': max_depth,
               'min_samples_split': min_samples_split,
               'min_samples_leaf': min_samples_leaf,
               'bootstrap': bootstrap}


# Random search of parameters, using 3 fold cross validation,
# search across 100 different combinations, and use all available cores
rf = RandomizedSearchCV(estimator = rf, param_distributions = random_grid, n_iter = 5, cv = 4, verbose=2, random_state=42, n_jobs = -1)
# Fit the random search model
rf.fit(train_features, train_labels)

rf.best_params_


def evaluate(model, test_features, test_labels):
    predictions = model.predict(test_features)
    errors = abs(predictions - test_labels)
    mape = 100 * np.mean(errors / test_labels)
    accuracy = 100 - mape
    return accuracy

# K folding
rf_accuracy = evaluate(rf, test_features, test_labels)

best_random = rf.best_estimator_
random_accuracy = evaluate(best_random, test_features, test_labels)

print('Improvement of {:0.2f}%.'.format(100 * (random_accuracy - rf_accuracy) / rf_accuracy))

model_path = os.path.join(PROJECT_DIR, 'models', 'randomForest.pkl')
print("Saving model.")
joblib.dump(rf, model_path)
print("Model successfully saved at %s" % model_path)