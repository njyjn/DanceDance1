import os
import json
import csv
import numpy as np
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


labels_dict = {
    0: 'hunch', 1: 'cowboy', 2: 'crab', 3: 'chicken', 4: 'raffles'
}

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
data_x_train_path = os.path.join(PROJECT_DIR, 'data', 'Train')
x_train_file = os.path.join(data_x_train_path, 'X_train.txt')
data_raw_path = os.path.join(PROJECT_DIR, 'data', 'raw')
label_file = os.path.join(data_raw_path, 'labels.txt')
processed_data_path = os.path.join(PROJECT_DIR, 'data', 'processed')

model_path = os.path.join(PROJECT_DIR, 'models', 'firstmodel.h5')
model = load_model(model_path)
n_features = 18
# reshape data into time steps of sub-sequences
n_steps, n_length = 4, 15
# for i in range(len(test_samples)):
#     test_samples[i] = test_samples[i].reshape((1, n_steps, n_length, n_features))


def normalise(x, minx, maxx):
    new_x = 2*(x-minx)/(maxx-minx) - 1
    return new_x


filename = "jiahao_raffles.txt"
print(filename)
with open(os.path.join(data_raw_path, filename), 'r') as data_file:
    lines = data_file.readlines()
    count = 0
    data_line = []
    data_all = []
    for line in lines:
        line_raw = line.strip()
        data_line_groups = line.split(" ")
        count = count + 1
        if len(data_line_groups) == 5:
            arr_str = data_line_groups[-1]
            arr_str = arr_str[:-1]
            arr = arr_str.split(",")
            if arr[0] == '':
                continue
            arr = [int(data) for data in arr]
            data_line.extend(arr)
        if len(data_line) == 18:
            data_all.append(data_line)
            data_line = []
            count = 0
    print(len(data_all))
    data_to_test = []
    for i in range(len(data_all)):
        if i in range(60, 120):
            data_to_test.append(data_all[i])

    for arr in data_to_test:
        for i in range(len(arr)):
            if i < 3:
                arr[i] = normalise(arr[i], -2000, 2000)
            elif i in range(3, 6):
                arr[i] = normalise(arr[i], -250000, 250000)
            elif i in range(6, 9):
                arr[i] = normalise(arr[i], -2000, 2000)
            elif i in range(9, 12):
                arr[i] = normalise(arr[i], -250000, 250000)
            elif i in range(12, 15):
                arr[i] = normalise(arr[i], -2000, 2000)
            elif i in range(15, 18):
                arr[i] = normalise(arr[i], -250000, 250000)
    print(data_to_test)

    # data1_acc_x = []
    # data1_acc_y = []
    # data1_acc_z = []
    # data1_gyro_x = []
    # data1_gyro_y = []
    # data1_gyro_z = []
    # data2_acc_x = []
    # data2_acc_y = []
    # data2_acc_z = []
    # data2_gyro_x = []
    # data2_gyro_y = []
    # data2_gyro_z = []
    # data3_acc_x = []
    # data3_acc_y = []
    # data3_acc_z = []
    # data3_gyro_x = []
    # data3_gyro_y = []
    # data3_gyro_z = []
    #
    # for arr in data_to_test:
    #     data1_acc_x.append(arr[0])
    #     data1_acc_y.append(arr[1])
    #     data1_acc_z.append(arr[2])
    #     data1_gyro_x.append(arr[3])
    #     data1_gyro_y.append(arr[4])
    #     data1_gyro_z.append(arr[5])
    #     data2_acc_x.append(arr[6])
    #     data2_acc_y.append(arr[7])
    #     data2_acc_z.append(arr[8])
    #     data2_gyro_x.append(arr[9])
    #     data2_gyro_y.append(arr[10])
    #     data2_gyro_z.append(arr[11])
    #     data3_acc_x.append(arr[12])
    #     data3_acc_y.append(arr[13])
    #     data3_acc_z.append(arr[14])
    #     data3_gyro_x.append(arr[15])
    #     data3_gyro_y.append(arr[16])
    #     data3_gyro_z.append(arr[17])


    # test_sample = [
    #     data1_acc_x, data1_acc_y, data1_acc_z, data2_acc_x, data2_acc_y, data2_acc_z, data3_acc_x, data3_acc_y,
    #     data3_acc_z, data1_gyro_x, data1_gyro_y, data1_gyro_z, data2_gyro_x, data2_gyro_y, data2_gyro_z,
    #     data3_gyro_x, data3_gyro_y, data3_gyro_z
    # ]

    arr_data = []
    for array in data_to_test:
        arr_raw = []
        arr_raw += [
            array[0], array[1], array[2], array[6], array[7], array[8], array[12], array[13], array[14], array[3],
            array[4], array[5], array[9], array[10], array[11], array[15], array[16], array[17]
        ]
        arr_data.append(arr_raw)
    # print(arr_data)
    test_sample = arr_data
    # print(len(test_sample))
    # print(len(test_sample[0]))

    test_sample = np.array(test_sample)
    # print(test_sample.shape)
    print(filename)

    test_sample = test_sample.reshape(1, n_steps, n_length, n_features)
    print(test_sample.shape)
    result = model.predict(test_sample, batch_size=96, verbose=0)
    pprint(result[0])
    result_int = int(np.argmax(result[0]))
    pprint(labels_dict[result_int] + ' ' + str(result_int))


filename = "melvin_cowboy.txt"
print(filename)
with open(os.path.join(data_raw_path, filename), 'r') as data_file:
    lines = data_file.readlines()
    count = 0
    data_line = []
    data_all = []
    for line in lines:
        line_raw = line.strip()
        data_line_groups = line.split(" ")
        count = count + 1
        if len(data_line_groups) == 5:
            arr_str = data_line_groups[-1]
            arr_str = arr_str[:-1]
            arr = arr_str.split(",")
            if arr[0] == '':
                continue
            arr = [int(data) for data in arr]
            data_line.extend(arr)
        if len(data_line) == 18:
            data_all.append(data_line)
            data_line = []
            count = 0
    data_to_test = []
    for i in range(len(data_all)):
        if i in range(2060, 2120):
            data_to_test.append(data_all[i])

    for arr in data_to_test:
        for i in range(len(arr)):
            if i < 3:
                arr[i] = normalise(arr[i], -2000, 2000)
            elif i in range(3, 6):
                arr[i] = normalise(arr[i], -250000, 250000)
            elif i in range(6, 9):
                arr[i] = normalise(arr[i], -2000, 2000)
            elif i in range(9, 12):
                arr[i] = normalise(arr[i], -250000, 250000)
            elif i in range(12, 15):
                arr[i] = normalise(arr[i], -2000, 2000)
            elif i in range(15, 18):
                arr[i] = normalise(arr[i], -250000, 250000)

    arr_data = []
    for array in data_to_test:
        arr_raw = []
        arr_raw += [
            array[0], array[1], array[2], array[6], array[7], array[8], array[12], array[13], array[14], array[3],
            array[4], array[5], array[9], array[10], array[11], array[15], array[16], array[17]
        ]
        arr_data.append(arr_raw)
    test_sample = arr_data

    test_sample = np.array(test_sample)

    test_sample = test_sample.reshape(1, n_steps, n_length, n_features)
    result = model.predict(test_sample, batch_size=96, verbose=0)
    result_int = int(np.argmax(result[0]))
    pprint(labels_dict[result_int] + ' ' + str(result_int))

filename = "zhiwei_chicken.txt"
print(filename)
with open(os.path.join(data_raw_path, filename), 'r') as data_file:
    lines = data_file.readlines()
    count = 0
    data_line = []
    data_all = []
    for line in lines:
        line_raw = line.strip()
        data_line_groups = line.split(" ")
        count = count + 1
        if len(data_line_groups) == 5:
            arr_str = data_line_groups[-1]
            arr_str = arr_str[:-1]
            arr = arr_str.split(",")
            if arr[0] == '':
                continue
            arr = [int(data) for data in arr]
            data_line.extend(arr)
        if len(data_line) == 18:
            data_all.append(data_line)
            data_line = []
            count = 0
    data_to_test = []
    for i in range(len(data_all)):
        if i in range(2060, 2120):
            data_to_test.append(data_all[i])

    for arr in data_to_test:
        for i in range(len(arr)):
            if i < 3:
                arr[i] = normalise(arr[i], -2000, 2000)
            elif i in range(3, 6):
                arr[i] = normalise(arr[i], -250000, 250000)
            elif i in range(6, 9):
                arr[i] = normalise(arr[i], -2000, 2000)
            elif i in range(9, 12):
                arr[i] = normalise(arr[i], -250000, 250000)
            elif i in range(12, 15):
                arr[i] = normalise(arr[i], -2000, 2000)
            elif i in range(15, 18):
                arr[i] = normalise(arr[i], -250000, 250000)

    arr_data = []
    for array in data_to_test:
        arr_raw = []
        arr_raw += [
            array[0], array[1], array[2], array[6], array[7], array[8], array[12], array[13], array[14], array[3],
            array[4], array[5], array[9], array[10], array[11], array[15], array[16], array[17]
        ]
        arr_data.append(arr_raw)
    test_sample = arr_data

    test_sample = np.array(test_sample)

    test_sample = test_sample.reshape(1, n_steps, n_length, n_features)
    result = model.predict(test_sample, batch_size=96, verbose=0)
    result_int = int(np.argmax(result[0]))
    pprint(labels_dict[result_int] + ' ' + str(result_int))

filename = "justin_crab.txt"
print(filename)
with open(os.path.join(data_raw_path, filename), 'r') as data_file:
    lines = data_file.readlines()
    count = 0
    data_line = []
    data_all = []
    for line in lines:
        line_raw = line.strip()
        data_line_groups = line.split(" ")
        count = count + 1
        if len(data_line_groups) == 5:
            arr_str = data_line_groups[-1]
            arr_str = arr_str[:-1]
            arr = arr_str.split(",")
            if arr[0] == '':
                continue
            arr = [int(data) for data in arr]
            data_line.extend(arr)
        if len(data_line) == 18:
            data_all.append(data_line)
            data_line = []
            count = 0
    data_to_test = []
    for i in range(len(data_all)):
        if i in range(160, 220):
            data_to_test.append(data_all[i])

    for arr in data_to_test:
        for i in range(len(arr)):
            if i < 3:
                arr[i] = normalise(arr[i], -2000, 2000)
            elif i in range(3, 6):
                arr[i] = normalise(arr[i], -250000, 250000)
            elif i in range(6, 9):
                arr[i] = normalise(arr[i], -2000, 2000)
            elif i in range(9, 12):
                arr[i] = normalise(arr[i], -250000, 250000)
            elif i in range(12, 15):
                arr[i] = normalise(arr[i], -2000, 2000)
            elif i in range(15, 18):
                arr[i] = normalise(arr[i], -250000, 250000)

    arr_data = []
    for array in data_to_test:
        arr_raw = []
        arr_raw += [
            array[0], array[1], array[2], array[6], array[7], array[8], array[12], array[13], array[14], array[3],
            array[4], array[5], array[9], array[10], array[11], array[15], array[16], array[17]
        ]
        arr_data.append(arr_raw)
    test_sample = arr_data

    test_sample = np.array(test_sample)

    test_sample = test_sample.reshape(1, n_steps, n_length, n_features)
    result = model.predict(test_sample, batch_size=96, verbose=0)
    result_int = int(np.argmax(result[0]))
    pprint(labels_dict[result_int] + ' ' + str(result_int))

filename = "melvin_hunch.txt"
print(filename)
with open(os.path.join(data_raw_path, filename), 'r') as data_file:
    lines = data_file.readlines()
    count = 0
    data_line = []
    data_all = []
    for line in lines:
        line_raw = line.strip()
        data_line_groups = line.split(" ")
        count = count + 1
        if len(data_line_groups) == 5:
            arr_str = data_line_groups[-1]
            arr_str = arr_str[:-1]
            arr = arr_str.split(",")
            if arr[0] == '':
                continue
            arr = [int(data) for data in arr]
            data_line.extend(arr)
        if len(data_line) == 18:
            data_all.append(data_line)
            data_line = []
            count = 0
    data_to_test = []
    for i in range(len(data_all)):
        if i in range(160, 220):
            data_to_test.append(data_all[i])

    for arr in data_to_test:
        for i in range(len(arr)):
            if i < 3:
                arr[i] = normalise(arr[i], -2000, 2000)
            elif i in range(3, 6):
                arr[i] = normalise(arr[i], -250000, 250000)
            elif i in range(6, 9):
                arr[i] = normalise(arr[i], -2000, 2000)
            elif i in range(9, 12):
                arr[i] = normalise(arr[i], -250000, 250000)
            elif i in range(12, 15):
                arr[i] = normalise(arr[i], -2000, 2000)
            elif i in range(15, 18):
                arr[i] = normalise(arr[i], -250000, 250000)

    arr_data = []
    for array in data_to_test:
        arr_raw = []
        arr_raw += [
            array[0], array[1], array[2], array[6], array[7], array[8], array[12], array[13], array[14], array[3],
            array[4], array[5], array[9], array[10], array[11], array[15], array[16], array[17]
        ]
        arr_data.append(arr_raw)
    test_sample = arr_data

    test_sample = np.array(test_sample)

    test_sample = test_sample.reshape(1, n_steps, n_length, n_features)
    result = model.predict(test_sample, batch_size=96, verbose=0)
    result_int = int(np.argmax(result[0]))
    pprint(labels_dict[result_int] + ' ' + str(result_int))

filename = "zhiwei_hunch.txt"
print(filename)
with open(os.path.join(data_raw_path, filename), 'r') as data_file:
    lines = data_file.readlines()
    count = 0
    data_line = []
    data_all = []
    for line in lines:
        line_raw = line.strip()
        data_line_groups = line.split(" ")
        count = count + 1
        if len(data_line_groups) == 5:
            arr_str = data_line_groups[-1]
            arr_str = arr_str[:-1]
            arr = arr_str.split(",")
            if arr[0] == '':
                continue
            arr = [int(data) for data in arr]
            data_line.extend(arr)
        if len(data_line) == 18:
            data_all.append(data_line)
            data_line = []
            count = 0
    data_to_test = []
    for i in range(len(data_all)):
        if i in range(160, 220):
            data_to_test.append(data_all[i])

    for arr in data_to_test:
        for i in range(len(arr)):
            if i < 3:
                arr[i] = normalise(arr[i], -2000, 2000)
            elif i in range(3, 6):
                arr[i] = normalise(arr[i], -250000, 250000)
            elif i in range(6, 9):
                arr[i] = normalise(arr[i], -2000, 2000)
            elif i in range(9, 12):
                arr[i] = normalise(arr[i], -250000, 250000)
            elif i in range(12, 15):
                arr[i] = normalise(arr[i], -2000, 2000)
            elif i in range(15, 18):
                arr[i] = normalise(arr[i], -250000, 250000)

    arr_data = []
    for array in data_to_test:
        arr_raw = []
        arr_raw += [
            array[0], array[1], array[2], array[6], array[7], array[8], array[12], array[13], array[14], array[3],
            array[4], array[5], array[9], array[10], array[11], array[15], array[16], array[17]
        ]
        arr_data.append(arr_raw)
    test_sample = arr_data

    test_sample = np.array(test_sample)

    test_sample = test_sample.reshape(1, n_steps, n_length, n_features)
    result = model.predict(test_sample, batch_size=96, verbose=0)
    result_int = int(np.argmax(result[0]))
    pprint(labels_dict[result_int] + ' ' + str(result_int))

filename = "zhiwei_chicken.txt"
print(filename)
with open(os.path.join(data_raw_path, filename), 'r') as data_file:
    lines = data_file.readlines()
    count = 0
    data_line = []
    data_all = []
    for line in lines:
        line_raw = line.strip()
        data_line_groups = line.split(" ")
        count = count + 1
        if len(data_line_groups) == 5:
            arr_str = data_line_groups[-1]
            arr_str = arr_str[:-1]
            arr = arr_str.split(",")
            if arr[0] == '':
                continue
            arr = [int(data) for data in arr]
            data_line.extend(arr)
        if len(data_line) == 18:
            data_all.append(data_line)
            data_line = []
            count = 0
    data_to_test = []
    for i in range(len(data_all)):
        if i in range(560, 620):
            data_to_test.append(data_all[i])

    for arr in data_to_test:
        for i in range(len(arr)):
            if i < 3:
                arr[i] = normalise(arr[i], -2000, 2000)
            elif i in range(3, 6):
                arr[i] = normalise(arr[i], -250000, 250000)
            elif i in range(6, 9):
                arr[i] = normalise(arr[i], -2000, 2000)
            elif i in range(9, 12):
                arr[i] = normalise(arr[i], -250000, 250000)
            elif i in range(12, 15):
                arr[i] = normalise(arr[i], -2000, 2000)
            elif i in range(15, 18):
                arr[i] = normalise(arr[i], -250000, 250000)

    arr_data = []
    for array in data_to_test:
        arr_raw = []
        arr_raw += [
            array[0], array[1], array[2], array[6], array[7], array[8], array[12], array[13], array[14], array[3],
            array[4], array[5], array[9], array[10], array[11], array[15], array[16], array[17]
        ]
        arr_data.append(arr_raw)
    test_sample = arr_data

    test_sample = np.array(test_sample)

    test_sample = test_sample.reshape(1, n_steps, n_length, n_features)
    result = model.predict(test_sample, batch_size=96, verbose=0)
    result_int = int(np.argmax(result[0]))
    pprint(labels_dict[result_int] + ' ' + str(result_int))
