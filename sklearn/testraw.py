import os
import numpy as np
from features_extraction import extract_features
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.model_selection import StratifiedKFold
from sklearn.svm import SVC
from sklearn.metrics import confusion_matrix
import os
from sklearn.preprocessing import StandardScaler
from sklearn.externals import joblib

labels_dict = {
    'chicken': 0, 'cowboy': 1, 'crab': 2, 'hunch': 3, 'raffles': 4
}

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
data_x_train_path = os.path.join(PROJECT_DIR, 'dance-dance-software', 'HAPT Data Set', 'Final')
x_train_file = os.path.join(data_x_train_path, 'X_train.txt')
data_raw_path = os.path.join(PROJECT_DIR, 'dance-dance-software', 'HAPT Data Set', 'Final')


def normalise(x, minx, maxx):
    new_x = 2*(x-minx)/(maxx-minx) - 1
    return new_x


filename = "jiahao_crab.txt"
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

    for arr in data_all:
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
    data_to_test = []
    for i in range(len(data_all)):
        if i in range(0, 60):
            # print(data_all[i])
            data_to_test.append(data_all[i])
    print(len(data_to_test[0]))

    features = []
    data_line = extract_features(np.asarray(data_to_test))
    features.append(data_line)

    features = np.array(features)
    print(features.shape)

    model_path_knn = os.path.join(PROJECT_DIR, 'dance-dance-software', 'models', 'kNN.pkl')
    model_path_rf = os.path.join(PROJECT_DIR, 'dance-dance-software', 'models', 'randomForest.pkl')
    model_path_svm = os.path.join(PROJECT_DIR, 'dance-dance-software', 'models', 'svm.pkl')
    rf = joblib.load(model_path_rf)
    knn = joblib.load(model_path_knn)
    svm = joblib.load(model_path_svm)

    # print(features)
    # sc = StandardScaler()
    # to_test = features[0].reshape(1, -1)
    # print(to_test)
    # X_train_array = sc.fit_transform(features)
    # Assign the scaled data to a DataFrame & use the index and columns arguments to keep your original indices and
    # column names:
    train_features = pd.DataFrame(features)
    # Center test data with the μ & σ computed (fitted) on training data

    print(train_features.shape)
    prediction_knn = knn.predict(features)
    prediction_rf = rf.predict(features)
    prediction_svm = svm.predict(features)
    pred_list = []
    pred_list.append(prediction_knn[0])
    pred_list.append(prediction_rf[0])
    pred_list.append(prediction_svm[0])

    from collections import Counter

    most_common, num_most_common = Counter(pred_list).most_common(1)[0]
    if num_most_common >= 2:
        print(most_common)

    # if (prediction_knn == prediction_rf == prediction_svm):
        # print(prediction_knn)
    # print(prediction_knn)
    # print(prediction_rf)
    # print(prediction_svm)






