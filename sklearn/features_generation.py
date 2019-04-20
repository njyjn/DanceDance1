import pandas as pd
import numpy as np
import os
from features_extraction import extract_features

labels = [
    'chicken', 'cowboy', 'crab', 'hunch', 'raffles'
]

labels_dict = {
    'chicken': 0, 'cowboy': 1, 'crab': 2, 'hunch': 3, 'raffles': 4
}

unavailable_labels = [
    'lie_to_sit', 'stand_to_lie'
]


PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
data_processed_path = os.path.join(PROJECT_DIR, 'dance-dance-software', 'HAPT Data Set', 'processed-pre-midterm')


# To apply overlapping sliding window
def create_windows(file_path, window_size, overlap):
    df = pd.read_csv(file_path, header=None)
    data_readings = df.values  # change to numpy array
    data_segments = []
    label_segments = []

    # window_size = 200, overlap at 50% = 100, 50hz, 4s, 200 windows for 4s each 0.02s,
    # shape of data_readings is (len(data_readings), 6)
    for i in range(int(len(data_readings)/overlap)-1):
        data_segments.append(data_readings[i*overlap:((i*overlap)+(window_size)), 0:18])
        file_name_split = file_path.split('/')
        file_name = file_name_split[-1]
        label_name = file_name[:-6]
        print(file_name[:-6])
        label_segments.append(labels_dict[label_name])
    return data_segments, label_segments


data_for_extraction = []
labels_for_extraction = []

for j in range(len(labels_dict)):
    for i in range(5):
        i_str = str(i+1)
        if len(i_str) is 1:
            i_str = '0' + i_str

        if i_str == '28' and labels[j] in unavailable_labels:
            continue
        readings, label = create_windows(os.path.join(data_processed_path, (labels[j] + i_str + ".csv")), 60, 30)
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
features_df.to_csv(data_csv_filename, header=[
    "val1", "val2", "val3", "val4", "val5", "val6", "val7", "val8", "val9", "val10", "val11", "val12", "val13", "val14",
    "val15", "val16", "val17", "val18", "val19", "val20", "val21", "val22", "val23", "val24", "val25", "val26", "val27",
    "val28", "val29", "val30", "val31", "val32", "val33", "val34", "val35", "val36", "val37", "val38", "val39", "val40",
    "val41", "val42", "val43", "val44", "val45", "val46", "val47", "val48", "val49", "val50", "val51", "val52", "val53",
    "val54", "val55", "val56", "val57", "val58", "val59", "val60", "val61", "val62", "val63", "val64", "val65", "val66",
    "val67", "val68", "val69", "val70", "val71", "val72", "dance"], index=None, sep=',')
labels_df = pd.DataFrame(labels_for_extraction)
labels_df.to_csv(labels_csv_filename, header=None, index=None)


