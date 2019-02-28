import os
import itertools
import keras
import numpy as np
from numpy import mean
from numpy import std
from numpy import dstack
from pandas import read_csv
from keras.models import load_model
from keras.utils import to_categorical
import sklearn.model_selection
from sklearn.metrics import confusion_matrix
import pandas as pd
import matplotlib.pyplot as plt
import math
from pprint import pprint


labels = [
    'walking', 'walking_upstairs', 'walking_downstairs', 'sitting', 'standing', 'laying', 'stand_to_sit', 'sit_to_stand'
    , 'sit_to_lie', 'lie_to_sit', 'stand_to_lie', 'lie_to_stand'
]


# load a single file as a numpy array
def load_file(filepath):
    dataframe = read_csv(filepath, header=None)
    return dataframe.values


# load a list of files and return as a 3d numpy array
def load_group(filenames, prefix=''):
    loaded = list()
    for name in filenames:
        data = load_file(prefix + name)
        loaded.append(data)
    # stack group so that features are the 3rd dimension
    loaded = dstack(loaded)
    return loaded


# load a dataset group, such as train or test
def load_dataset_group(group, prefix=''):
    filepath = group + '\\'
    # load all 6 files as a single array
    filenames = list()
    # acceleration
    filenames += ['acc_x.csv', 'acc_y.csv', 'acc_z.csv']
    # body gyroscope
    filenames += ['gyro_x.csv', 'gyro_y.csv', 'gyro_z.csv']
    # load input data
    X = load_group(filenames, filepath)
    # load class output
    y = load_file(filepath + 'labels.csv')

    return X, y


PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
data_accx = load_file(os.path.join(PROJECT_DIR, 'data', 'keras_datasets') + '\\' + 'acc_x.csv')
pprint(data_accx[0][0])
data_accy = load_file(os.path.join(PROJECT_DIR, 'data', 'keras_datasets') + '\\' + 'acc_y.csv')
pprint(data_accy[0][0])
data_accz = load_file(os.path.join(PROJECT_DIR, 'data', 'keras_datasets') + '\\' + 'acc_z.csv')
pprint(data_accz[0][0])
data_gyrox = load_file(os.path.join(PROJECT_DIR, 'data', 'keras_datasets') + '\\' + 'gyro_x.csv')
pprint(data_gyrox[0][0])
data_gyroy = load_file(os.path.join(PROJECT_DIR, 'data', 'keras_datasets') + '\\' + 'gyro_y.csv')
pprint(data_gyroy[0][0])
data_gyroz = load_file(os.path.join(PROJECT_DIR, 'data', 'keras_datasets') + '\\' + 'gyro_z.csv')
pprint(data_gyroz[0][0])
label_data = load_file(os.path.join(PROJECT_DIR, 'data', 'keras_datasets') + '\\' + 'labels.csv')

print(len(data_gyrox))
test_samples = []
test_labels = []

for j in range(6000):
    random_number = np.random.randint(0, 12190)
    test_acc_x = data_accx[random_number]
    test_acc_y = data_accy[random_number]
    test_acc_z = data_accz[random_number]
    test_gyro_x = data_gyrox[random_number]
    test_gyro_y = data_gyroy[random_number]
    test_gyro_z = data_gyroz[random_number]
    test_arr = list()
    for i in range(len(test_acc_x)):
        sub_arr = list()
        sub_arr.append(test_acc_x[i])
        sub_arr.append(test_acc_y[i])
        sub_arr.append(test_acc_z[i])
        sub_arr.append(test_gyro_x[i])
        sub_arr.append(test_gyro_y[i])
        sub_arr.append(test_gyro_z[i])
        test_arr.append(sub_arr)
    test_samples.append(test_arr)
    test_labels.append(label_data[random_number])

model_path = os.path.join(PROJECT_DIR, 'models', 'forthmodel.h5')
model = load_model(model_path)
# test_matrix = np.array(test_arr)
test_samples = np.array(test_samples)

n_features = 6
# reshape data into time steps of sub-sequences
n_steps, n_length = 4, 32
# for i in range(len(test_samples)):
#     test_samples[i] = test_samples[i].reshape((1, n_steps, n_length, n_features))

test_samples = test_samples.reshape(6000, n_steps, n_length, n_features)
results = model.predict(test_samples, batch_size=64, verbose=0)
# pprint(result[0])
# result_int = int(np.argmax(result[0]))
# pprint(labels[result_int] + ' ' + str(result_int))

rounded_predictions = []
for i in results:
    rounded_predictions.append(np.argmax(i))

cm = confusion_matrix(test_labels, rounded_predictions)
print(type(test_labels))
print(type(rounded_predictions))
# errors = abs(rounded_predictions - test_labels)
errors = []
for i in range(len(rounded_predictions)):
    errors.append(abs(rounded_predictions[i]-test_labels[i][0]))

num_errors = 0
for x in errors:
    if x == 1:
        num_errors += 1


score = 1.0 - (num_errors / len(test_labels))
print(score)

# score = (100* errors/(test_labels + 1))
# accuracy = 100-np.mean(score)
# print(accuracy)


def plot_confusion_matrix(cm, classes,
                          normalize=False,
                          title='Confusion matrix',
                          cmap=plt.cm.Blues):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')

    print(cm)

    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    fmt = '.2f' if normalize else 'd'
    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, format(cm[i, j], fmt),
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    plt.tight_layout()


# Plot non-normalized confusion matrix
plt.figure()
plot_confusion_matrix(cm, classes=labels,
                      title='Confusion matrix, without normalization')
#
# # Plot normalized confusion matrix
# plt.figure()
# plot_confusion_matrix(cnf_matrix, classes=labels, normalize=True,
#                       title='Normalized confusion matrix')
#
plt.show()
