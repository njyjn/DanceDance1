import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.model_selection import StratifiedKFold
from sklearn.svm import SVC
from sklearn.metrics import confusion_matrix
import os
from sklearn.preprocessing import StandardScaler
from sklearn.externals import joblib


def evaluate(model, test_features, test_labels):
    predictions = model.predict(test_features)
    errors = abs(predictions - test_labels)
    mape = 100 * np.mean(errors / test_labels)
    accuracy = 100 - mape
    return accuracy


PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
data_processed_path = os.path.join(PROJECT_DIR, 'data', 'processed')
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
train_features, test_features, train_labels, test_labels = train_test_split(features, labels, test_size=0.2,
                                                                            random_state=42)
# print('Training Features Shape:', train_features.shape)
# print('Training Labels Shape:', train_labels.shape)
# print('Testing Features Shape:', test_features.shape)
# print('Testing Labels Shape:', test_labels.shape)

# Instantiate svm model of multi-class according to a one-vs-one scheme.
model = SVC()

sc = StandardScaler()
X_train_array = sc.fit_transform(train_features)
# Assign the scaled data to a DataFrame & use the index and columns arguments to keep your original indices and
# column names:
train_features = pd.DataFrame(X_train_array)
# Center test data with the μ & σ computed (fitted) on training data
X_test_array = sc.transform(test_features)
test_features = pd.DataFrame(X_test_array)

# Train the model on training data
model.fit(train_features, train_labels)

# Use the forest's predict method on the test data
predictions = model.predict(test_features)

# Calculate the absolute errors
errors = abs(predictions - test_labels)

# Calculate mean absolute percentage error (MAPE)
mape = 100 * (errors / test_labels)

# Calculate and display accuracy
accuracy = 100 - np.mean(mape)
print('Accuracy:', accuracy, '%.')

# Print out confusion matrix
conf_mat = confusion_matrix(test_labels, predictions)
print(conf_mat)

model_path = os.path.join(PROJECT_DIR, 'models', 'svm.pkl')
# joblib.dump(model, model_path)
print("Model successfully saved at %s" % model_path)

# K folding
svm_accuracy = evaluate(model, test_features, test_labels)

saved_model = joblib.load(model_path)

train_features, test_features, train_labels, test_labels = train_test_split(features, labels, test_size=0.2,
                                                                            random_state=42)

# Use the forest's predict method on the test data
predictions = saved_model.predict(test_features)

# Calculate the absolute errors
errors = abs(predictions - test_labels)

# Calculate mean absolute percentage error (MAPE)
mape = 100 * (errors / (test_labels))

# Calculate and display accuracy
accuracy = 100 - np.mean(mape)
print('Accuracy:', accuracy, '%.')

# Print out confusion matrix
conf_mat = confusion_matrix(test_labels, predictions)
print(conf_mat)

