import os
import numpy as np
from numpy import mean
from numpy import std
from numpy import dstack
from pandas import read_csv
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Flatten
from keras.layers import Dropout
from keras.layers import LSTM
from keras.layers import TimeDistributed
from keras.layers.convolutional import Conv1D
from keras.layers.convolutional import MaxPooling1D
from keras.models import load_model
from keras.utils import to_categorical
import sklearn.model_selection
import pandas as pd

# load a single file as a numpy array
def load_file(filepath):
    dataframe = read_csv(filepath)
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


# load the dataset, returns train and test X and y elements
def load_dataset(prefix=''):
    # load all train
    trainX, trainy = load_dataset_group(os.path.join(PROJECT_DIR, 'data', 'keras_datasets'))

    return trainX, trainy


# fit and evaluate a model
def evaluate_model(model, trainX, trainy, testX, testy):
    # define model
    verbose, epochs, batch_size = 0, 25, 64
    n_timesteps, n_features, n_outputs = trainX.shape[1], trainX.shape[2], trainy.shape[1]

    # reshape data into time steps of sub-sequences
    n_steps, n_length = 4, 32
    testX = testX.reshape((testX.shape[0], n_steps, n_length, n_features))

    # evaluate model
    _, accuracy = model.evaluate(testX, testy, batch_size=batch_size, verbose=0)
    return accuracy


def train_model(trainX, trainy):
    # define model
    verbose, epochs, batch_size = 2, 80, 96
    n_timesteps, n_features, n_outputs = trainX.shape[1], trainX.shape[2], trainy.shape[1]

    # reshape data into time steps of sub-sequences
    n_steps, n_length = 4, 32
    trainX = trainX.reshape((trainX.shape[0], n_steps, n_length, n_features))
    # define model
    model = Sequential()
    model.add(TimeDistributed(Conv1D(filters=64, kernel_size=3, activation='relu'), input_shape=(None, n_length, n_features)))
    model.add(TimeDistributed(Conv1D(filters=64, kernel_size=3, activation='relu')))
    model.add(TimeDistributed(Dropout(0.5)))
    model.add(TimeDistributed(MaxPooling1D(pool_size=2)))
    model.add(TimeDistributed(Flatten()))
    model.add(LSTM(100))
    model.add(Dropout(0.5))
    model.add(Dense(100, activation='relu'))
    model.add(Dense(n_outputs, activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

    print(model.summary())
    # fit network
    model.fit(trainX, trainy, epochs=epochs, batch_size=batch_size, verbose=verbose)

    return model


# summarize scores
def summarize_results(scores):
    print(scores)
    m, s = mean(scores), std(scores)
    print('Accuracy: %.3f%% (+/-%.3f)' % (m, s))


PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
data_processed_path = os.path.join(PROJECT_DIR, 'data', 'keras_datasets')

data_x, data_y = load_dataset()
trainX, testX, trainY, testY = sklearn.model_selection.train_test_split(data_x, data_y, test_size=0.2, random_state=42)
trainY = to_categorical(trainY)
testY = to_categorical(testY)
print(trainX.shape, trainY.shape)
print(testX.shape, testY.shape)


# scores = list()
# for r in range(10):
#     score = evaluate_model(trainX, trainY, testX, testY)
#     score = score * 100.0
#     print('>#%d: %.3f' % (r+1, score))
#     scores.append(score)
# # summarize results
# summarize_results(scores)
model = train_model(trainX, trainY)
model_dir = os.path.join(PROJECT_DIR, 'models')
model_filepath = os.path.join(model_dir, 'firstmodel.h5')
model.save(model_filepath)
# model = load_model(model_filepath)

score = evaluate_model(model, trainX, trainY, testX, testY)
score = score * 100.0
print('%.3f' % score)

# n_timesteps, n_features, n_outputs = trainX.shape[1], trainX.shape[2], trainY.shape[1]
#
# # reshape data into time steps of sub-sequences
# n_steps, n_length = 4, 50
# test = test.reshape((1, n_steps, n_length, n_features))
# print(len(test))
# result = model.predict(test, batch_size=64, verbose=0)
# from pprint import pprint
# pprint(np.argmax(result[0]))
#
# pprint(result[0])
