import pandas as pd
import numpy as np
import os
from software.features_extraction import extract_features

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

    # window_size = 200, overlap at 50% = 100, 50hz, 4s, 200 windows for 4s each 0.02s,
    # shape of data_readings is (len(data_readings), 6)
    for i in range(int(len(data_readings)/overlap)-1):
        data_segments.append(data_readings[i*overlap:((i*overlap)+(window_size-1)), 0:6])
        file_name_split = file_path.split('/')
        file_name = file_name_split[-1]
        label_name = file_name[:-6]
        print(file_name[:-6])
        label_segments.append(labels_dict[label_name])
    return data_segments, label_segments


data_for_extraction = []
labels_for_extraction = []

for j in range(len(labels_dict)):
    for i in range(30):
        i_str = str(i+1)
        if len(i_str) is 1:
            i_str = '0' + i_str

        if i_str == '28' and labels[j] in unavailable_labels:
            continue
        readings, label = create_windows(os.path.join(data_processed_path, (labels[j] + i_str + ".csv")), 150, 75)
        data_for_extraction.extend(readings)
        labels_for_extraction.extend(label)

features = []
for i in range(len(data_for_extraction)):
    data_line = extract_features(np.asarray(data_for_extraction[i]))
    data_line.append(labels_for_extraction[i] + 1)
    features.append(data_line)


data_csv_filename = os.path.join(data_processed_path, 'dataFeatures.csv')
labels_csv_filename = os.path.join(data_processed_path, 'labelFeatures.csv')

features_df = pd.DataFrame(features)
features_df.to_csv(data_csv_filename, header=["val1", "val2", "val3", "val4", "val5", "val6", "val7", "val8", "val9", "val10",
                                              "val11", "val12", "val13", "val14", "val15", "val16", "val17", "val18", "val19", "val20",
                                              "val21", "val22", "val23", "val24", "dance"], index=None, sep=',')
labels_df = pd.DataFrame(labels_for_extraction)
labels_df.to_csv(labels_csv_filename, header=None, index=None)


