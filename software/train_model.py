from sklearn.externals import joblib
import os
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
from sklearn.preprocessing import StandardScaler
import pandas as pd
from collections import Counter

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
model_path_rf = os.path.join(PROJECT_DIR, 'models', 'randomForest.pkl')
model_path_kNN = os.path.join(PROJECT_DIR, 'models', 'kNN.pkl')
model_path_svm = os.path.join(PROJECT_DIR, 'models', 'svm.pkl')
rf = joblib.load(model_path_rf)
knn = joblib.load(model_path_kNN)
svm = joblib.load(model_path_svm)

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
data_processed_path = os.path.join(PROJECT_DIR, 'HAPT Data Set', 'processed')
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

sc = StandardScaler()
X_train_array = sc.fit_transform(train_features)
# Assign the scaled data to a DataFrame & use the index and columns arguments to keep your original indices and column names:
train_features = pd.DataFrame(X_train_array)
# Center test data with the μ & σ computed (fitted) on training data
X_test_array = sc.transform(test_features)
test_features = pd.DataFrame(X_test_array)

# Use the forest's predict method on the test data
predictions_rf = list(rf.predict(test_features))
predictions_kNN = list(knn.predict(test_features))
predictions_svm = list(svm.predict(test_features))

pred_list = []
pred_dance = []
test_labels_pred = []
test_labels = list(test_labels)

for i in range(0, 2582):
    pred_list.append(predictions_rf[i])
    pred_list.append(predictions_kNN[i])
    pred_list.append(predictions_svm[i])

    most_common, num_most_common = Counter(pred_list).most_common(1)[0]
    if num_most_common > 2:
        test_labels_pred.append(test_labels[i])
        pred_dance.append(most_common)

    pred_list = []

test_labels_pred = np.array(test_labels_pred)
test_labels = np.array(test_labels)

# Calculate the absolute errors
errors_rf = abs(predictions_rf - test_labels)
errors_kNN = abs(predictions_kNN - test_labels)
errors_svm = abs(predictions_svm - test_labels)

errors_pred = abs(pred_dance - test_labels_pred)

for i in range(len(pred_dance)):
    if pred_dance[i] != test_labels_pred[i]:
        print(pred_dance[i])
        print(test_labels_pred[i])

# Calculate mean absolute percentage error (MAPE)
mape_rf = 100 * (errors_rf / (test_labels))
mape_kNN = 100 * (errors_kNN / (test_labels))
mape_svm = 100 * (errors_svm / (test_labels))

mape_pred = abs(errors_pred - test_labels_pred)

# Calculate and display accuracy
accuracy_rf = 100 - np.mean(mape_rf)
accuracy_kNN = 100 - np.mean(mape_kNN)
accuracy_svm = 100 - np.mean(mape_svm)

accuracy_pred = 100 - np.mean(mape_pred)
print('Accuracy:', accuracy_pred, '%.')

if (accuracy_kNN > accuracy_rf and accuracy_kNN > accuracy_svm):
    print('RF Accuracy:', accuracy_kNN, '%.')
    conf_mat_kNN = confusion_matrix(test_labels, predictions_kNN)
    print(conf_mat_kNN)
elif (accuracy_rf > accuracy_kNN and accuracy_rf > accuracy_svm):
    print('KNN Accuracy:', accuracy_rf, '%.')
    conf_mat_rf = confusion_matrix(test_labels, predictions_rf)
    print(conf_mat_rf)
else:
    print('SVM Accuracy:', accuracy_svm, '%.')
    conf_mat_svm = confusion_matrix(test_labels, predictions_svm)
    print(conf_mat_svm)
