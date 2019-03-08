import pandas as pd
import numpy as np
import os

labels = [
    'walking', 'walking_upstairs', 'walking_downstairs', 'sitting', 'standing', 'laying', 'stand_to_sit', 'sit_to_stand'
    , 'sit_to_lie', 'lie_to_sit', 'stand_to_lie', 'lie_to_stand'
]

labels_dict = {
    'walking': 0, 'walking_upstairs': 1, 'walking_downstairs': 2, 'sitting': 3, 'standing': 4, 'laying': 5,
    'stand_to_sit': 6, 'sit_to_stand': 7, 'sit_to_lie': 8, 'lie_to_sit': 9, 'stand_to_lie': 10, 'lie_to_stand': 11
}

unavailable_labels = [
    'lie_to_sit', 'stand_to_lie'
]


PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
data_processed_path = os.path.join(PROJECT_DIR, 'data', 'processed')


# To apply overlapping sliding window
def create_windows(file_path, window_size, overlap):
    df = pd.read_csv(file_path, header=None)
    data_readings = df.values  # change to numpy array
    data_segments = []
    label_segments = []
    # window_size = 128, overlap at 50% = 64, 50hz, 2.56s, 128 windows for 2.56s each 0.02s,
    # shape of data_readings is (len(data_readings), 6)
    for i in range(int(len(data_readings)/overlap)-1):
        data_segments.append(data_readings[i*overlap:((i*overlap)+(window_size)), 0:6])
        file_name_split = file_path.split('\\')
        file_name = file_name_split[-1]
        label_name = file_name[:-6]
        label_segments.append(labels_dict[label_name])
    return data_segments, label_segments


# data_for_extraction = []
labels_for_extraction = []

data_acc_x = []
data_acc_y = []
data_acc_z = []
data_gyro_x = []
data_gyro_y = []
data_gyro_z = []

for j in range(len(labels_dict)):
    for i in range(30):
        i_str = str(i+1)
        if len(i_str) is 1:
            i_str = '0' + i_str

        if i_str == '28' and labels[j] in unavailable_labels:
            continue
        readings, label = create_windows(os.path.join(data_processed_path, (labels[j] + i_str + ".csv")), 128, 64)
        for k in range(len(readings)):
            acc_x = []
            acc_y = []
            acc_z = []
            gyro_x = []
            gyro_y = []
            gyro_z = []
            for l in range(len(readings[k])):
                acc_x.append(readings[k][l][0])
                acc_y.append(readings[k][l][1])
                acc_z.append(readings[k][l][2])
                gyro_x.append(readings[k][l][3])
                gyro_y.append(readings[k][l][4])
                gyro_z.append(readings[k][l][5])
            data_acc_x.append(acc_x)
            data_acc_y.append(acc_y)
            data_acc_z.append(acc_z)
            data_gyro_x.append(gyro_x)
            data_gyro_y.append(gyro_y)
            data_gyro_z.append(gyro_z)
        # data_for_extraction.extend(readings)
        labels_for_extraction.extend(label)

print(len(labels_for_extraction))
print(len(data_acc_x))

keras_data_path = os.path.join(PROJECT_DIR, 'data', 'keras_datasets')
acc_x_file = os.path.join(keras_data_path, 'acc_x.csv')
acc_y_file = os.path.join(keras_data_path, 'acc_y.csv')
acc_z_file = os.path.join(keras_data_path, 'acc_z.csv')
gyro_x_file = os.path.join(keras_data_path, 'gyro_x.csv')
gyro_y_file = os.path.join(keras_data_path, 'gyro_y.csv')
gyro_z_file = os.path.join(keras_data_path, 'gyro_z.csv')
labels_file = os.path.join(keras_data_path, 'labels.csv')


acc_x_df = pd.DataFrame(data_acc_x)
acc_x_df.to_csv(acc_x_file, header=None, index=None, sep=',')
acc_y_df = pd.DataFrame(data_acc_y)
acc_y_df.to_csv(acc_y_file, header=None, index=None, sep=',')
acc_z_df = pd.DataFrame(data_acc_z)
acc_z_df.to_csv(acc_z_file, header=None, index=None, sep=',')
gyro_x_df = pd.DataFrame(data_gyro_x)
gyro_x_df.to_csv(gyro_x_file, header=None, index=None, sep=',')
gyro_y_df = pd.DataFrame(data_gyro_y)
gyro_y_df.to_csv(gyro_y_file, header=None, index=None, sep=',')
gyro_z_df = pd.DataFrame(data_gyro_z)
gyro_z_df.to_csv(gyro_z_file, header=None, index=None, sep=',')
labels_df = pd.DataFrame(labels_for_extraction)
labels_df.to_csv(labels_file, header=None, index=None)


# accX_data = pd.read_csv(acc_x_file)
# accY_data = pd.read_csv(acc_y_file)
# accZ_data = pd.read_csv(acc_z_file)
# gyroX_data = pd.read_csv(gyro_x_file)
# gyroY_data = pd.read_csv(gyro_y_file)
# gyroZ_data = pd.read_csv(gyro_z_file)
#
# Y_data = pd.read_csv(os.path.join(data_processed_path, 'labelFeatures.csv'))
# X_data = X_data.values
# Y_data = Y_data.values
# trainX, testX, trainY, testY = sklearn.model_selection.train_test_split(X_data, Y_data, test_size=0.2, random_state=0)


# features = []
# for i in range(len(data_for_extraction)):
#     features.append(extract_features(np.asarray(data_for_extraction[i])))
#
#
# data_csv_filename = os.path.join(data_processed_path, 'dataFeatures.csv')
# labels_csv_filename = os.path.join(data_processed_path, 'labelFeatures.csv')

# features_df = pd.DataFrame(features)
# features_df.to_csv(data_csv_filename, header=None, index=None, sep=',')
# labels_df = pd.DataFrame(labels_for_extraction)
# labels_df.to_csv(labels_csv_filename, header=None, index=None)


