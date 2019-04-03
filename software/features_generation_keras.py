import pandas as pd
import numpy as np
import os

labels = [
    'walking', 'walking_upstairs', 'walking_downstairs', 'sitting', 'standing', 'laying', 'stand_to_sit', 'sit_to_stand'
    , 'sit_to_lie', 'lie_to_sit', 'stand_to_lie', 'lie_to_stand'
]

labels_dict = {
    'hunch': 0, 'cowboy': 1, 'crab': 2, 'chicken': 3, 'raffles': 4
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
    # window_size = 60, overlap at 50% = 30, 20hz, 3s, 60 windows for 3s each 0.05s,
    # shape of data_readings is (len(data_readings), 6)
    for i in range(int(len(data_readings)/overlap)-1):
        data_segments.append(data_readings[i*overlap:((i*overlap)+(window_size)), 0:18])
        file_name_split = file_path.split('\\')
        file_name = file_name_split[-1]
        label_name = file_name[:-5]
        label_names = file_name[:-4].split("_")
        label_name = label_names[-1]
        label_segments.append(labels_dict[label_name])
    return data_segments, label_segments


# data_for_extraction = []
labels_for_extraction = []

data1_acc_x = []
data1_acc_y = []
data1_acc_z = []
data1_gyro_x = []
data1_gyro_y = []
data1_gyro_z = []
data2_acc_x = []
data2_acc_y = []
data2_acc_z = []
data2_gyro_x = []
data2_gyro_y = []
data2_gyro_z = []
data3_acc_x = []
data3_acc_y = []
data3_acc_z = []
data3_gyro_x = []
data3_gyro_y = []
data3_gyro_z = []

# for j in range(len(labels_dict)):
for filename in os.listdir(data_processed_path):
    if filename.endswith(".csv"):
        # i_str = str(i+1)
        # if len(i_str) is 1:
        #     i_str = '0' + i_str
        #
        # if i_str == '28' and labels[j] in unavailable_labels:
        #     continue
        # readings, label = create_windows(os.path.join(data_processed_path, (labels[j] + i_str + ".csv")), 128, 64)

        readings, label = create_windows(os.path.join(data_processed_path, filename), 60, 30)

        for k in range(len(readings)):
            acc_x_1 = []
            acc_y_1 = []
            acc_z_1 = []
            gyro_x_1 = []
            gyro_y_1 = []
            gyro_z_1 = []
            acc_x_2 = []
            acc_y_2 = []
            acc_z_2 = []
            gyro_x_2 = []
            gyro_y_2 = []
            gyro_z_2 = []
            acc_x_3 = []
            acc_y_3 = []
            acc_z_3 = []
            gyro_x_3 = []
            gyro_y_3 = []
            gyro_z_3 = []
            # print(readings[k])
            for l in range(len(readings[k])):
                acc_x_1.append(readings[k][l][0])
                acc_y_1.append(readings[k][l][1])
                acc_z_1.append(readings[k][l][2])
                gyro_x_1.append(readings[k][l][3])
                gyro_y_1.append(readings[k][l][4])
                gyro_z_1.append(readings[k][l][5])
                acc_x_2.append(readings[k][l][6])
                acc_y_2.append(readings[k][l][7])
                acc_z_2.append(readings[k][l][8])
                gyro_x_2.append(readings[k][l][9])
                gyro_y_2.append(readings[k][l][10])
                gyro_z_2.append(readings[k][l][11])
                acc_x_3.append(readings[k][l][12])
                acc_y_3.append(readings[k][l][13])
                acc_z_3.append(readings[k][l][14])
                gyro_x_3.append(readings[k][l][15])
                gyro_y_3.append(readings[k][l][16])
                gyro_z_3.append(readings[k][l][17])
            data1_acc_x.append(acc_x_1)
            data1_acc_y.append(acc_y_1)
            data1_acc_z.append(acc_z_1)
            data1_gyro_x.append(gyro_x_1)
            data1_gyro_y.append(gyro_y_1)
            data1_gyro_z.append(gyro_z_1)
            data2_acc_x.append(acc_x_2)
            data2_acc_y.append(acc_y_2)
            data2_acc_z.append(acc_z_2)
            data2_gyro_x.append(gyro_x_2)
            data2_gyro_y.append(gyro_y_2)
            data2_gyro_z.append(gyro_z_2)
            data3_acc_x.append(acc_x_3)
            data3_acc_y.append(acc_y_3)
            data3_acc_z.append(acc_z_3)
            data3_gyro_x.append(gyro_x_3)
            data3_gyro_y.append(gyro_y_3)
            data3_gyro_z.append(gyro_z_3)
        # data_for_extraction.extend(readings)
        labels_for_extraction.extend(label)

print(len(labels_for_extraction))
print(len(data1_acc_x))
print(len(data2_acc_x))
print(len(data3_acc_x))
print(labels_for_extraction)

keras_data_path = os.path.join(PROJECT_DIR, 'data', 'keras_datasets')
acc_x1_file = os.path.join(keras_data_path, 'acc_x1.csv')
acc_y1_file = os.path.join(keras_data_path, 'acc_y1.csv')
acc_z1_file = os.path.join(keras_data_path, 'acc_z1.csv')
gyro_x1_file = os.path.join(keras_data_path, 'gyro_x1.csv')
gyro_y1_file = os.path.join(keras_data_path, 'gyro_y1.csv')
gyro_z1_file = os.path.join(keras_data_path, 'gyro_z1.csv')
labels_file = os.path.join(keras_data_path, 'labels.csv')
acc_x2_file = os.path.join(keras_data_path, 'acc_x2.csv')
acc_y2_file = os.path.join(keras_data_path, 'acc_y2.csv')
acc_z2_file = os.path.join(keras_data_path, 'acc_z2.csv')
gyro_x2_file = os.path.join(keras_data_path, 'gyro_x2.csv')
gyro_y2_file = os.path.join(keras_data_path, 'gyro_y2.csv')
gyro_z2_file = os.path.join(keras_data_path, 'gyro_z2.csv')
acc_x3_file = os.path.join(keras_data_path, 'acc_x3.csv')
acc_y3_file = os.path.join(keras_data_path, 'acc_y3.csv')
acc_z3_file = os.path.join(keras_data_path, 'acc_z3.csv')
gyro_x3_file = os.path.join(keras_data_path, 'gyro_x3.csv')
gyro_y3_file = os.path.join(keras_data_path, 'gyro_y3.csv')
gyro_z3_file = os.path.join(keras_data_path, 'gyro_z3.csv')


acc_x1_df = pd.DataFrame(data1_acc_x)
acc_x1_df.to_csv(acc_x1_file, header=None, index=None, sep=',')
acc_y1_df = pd.DataFrame(data1_acc_y)
acc_y1_df.to_csv(acc_y1_file, header=None, index=None, sep=',')
acc_z1_df = pd.DataFrame(data1_acc_z)
acc_z1_df.to_csv(acc_z1_file, header=None, index=None, sep=',')
gyro_x1_df = pd.DataFrame(data1_gyro_x)
gyro_x1_df.to_csv(gyro_x1_file, header=None, index=None, sep=',')
gyro_y1_df = pd.DataFrame(data1_gyro_y)
gyro_y1_df.to_csv(gyro_y1_file, header=None, index=None, sep=',')
gyro_z1_df = pd.DataFrame(data1_gyro_z)
gyro_z1_df.to_csv(gyro_z1_file, header=None, index=None, sep=',')
acc_x2_df = pd.DataFrame(data2_acc_x)
acc_x2_df.to_csv(acc_x2_file, header=None, index=None, sep=',')
acc_y2_df = pd.DataFrame(data2_acc_y)
acc_y2_df.to_csv(acc_y2_file, header=None, index=None, sep=',')
acc_z2_df = pd.DataFrame(data2_acc_z)
acc_z2_df.to_csv(acc_z2_file, header=None, index=None, sep=',')
gyro_x2_df = pd.DataFrame(data2_gyro_x)
gyro_x2_df.to_csv(gyro_x2_file, header=None, index=None, sep=',')
gyro_y2_df = pd.DataFrame(data2_gyro_y)
gyro_y2_df.to_csv(gyro_y2_file, header=None, index=None, sep=',')
gyro_z2_df = pd.DataFrame(data2_gyro_z)
gyro_z2_df.to_csv(gyro_z2_file, header=None, index=None, sep=',')
acc_x3_df = pd.DataFrame(data3_acc_x)
acc_x3_df.to_csv(acc_x3_file, header=None, index=None, sep=',')
acc_y3_df = pd.DataFrame(data3_acc_y)
acc_y3_df.to_csv(acc_y3_file, header=None, index=None, sep=',')
acc_z3_df = pd.DataFrame(data3_acc_z)
acc_z3_df.to_csv(acc_z3_file, header=None, index=None, sep=',')
gyro_x3_df = pd.DataFrame(data3_gyro_x)
gyro_x3_df.to_csv(gyro_x3_file, header=None, index=None, sep=',')
gyro_y3_df = pd.DataFrame(data3_gyro_y)
gyro_y3_df.to_csv(gyro_y3_file, header=None, index=None, sep=',')
gyro_z3_df = pd.DataFrame(data3_gyro_z)
gyro_z3_df.to_csv(gyro_z3_file, header=None, index=None, sep=',')
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


