import os
import json
import csv


label = {1: 'WALKING', 2: 'WALKING_UPSTAIRS', 3: 'WALKING_DOWNSTAIRS', 4: 'SITTING', 5: 'STANDING', 6: 'LAYING',
         7: 'STAND_TO_SIT', 8: 'SIT_TO_STAND', 9: 'SIT_TO_LIE', 10: 'LIE_TO_SIT', 11: 'STAND_TO_LIE', 12: 'LIE_TO_STAND'
         }

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
data_x_train_path = os.path.join(PROJECT_DIR, 'data', 'Train')
x_train_file = os.path.join(data_x_train_path, 'X_train.txt')
data_raw_path = os.path.join(PROJECT_DIR, 'data', 'raw')
label_file = os.path.join(data_raw_path, 'labels.txt')
processed_data_path = os.path.join(PROJECT_DIR, 'data', 'processed')


def normalise(x, minx, maxx):
    new_x = 2*(x-minx)/(maxx-minx) - 1
    return new_x


for filename in os.listdir(data_raw_path):
    if filename.endswith(".json"):
        name = filename[:-5]
        new_file_name = name + '.csv'
        new_data_path = os.path.join(processed_data_path, new_file_name)
        data = []
        last = ''
        print(filename)
        with open(os.path.join(data_raw_path, filename), 'r') as data_file:
            lines = data_file.readlines()
            last = lines[-1]
            print('last:')
            print(last)
            if last == '':
                last = lines[-2]
                print(last)
        with open(os.path.join(data_raw_path, filename), 'r') as data_file:

            count = 0
            for line in data_file:
                data_line = []
                if line != last:
                    line = line[:-2]
                else:
                    line = line[:-1]
                if count == 0:
                    line = line[1:]
                count = count + 1
                print(filename)
                print(line)
                print('hi')
                data_line_raw = json.loads(line)
                data_arr = data_line_raw['01']
                line = line[:-1]
                items = line.split(" ")
                print(data_arr)
                # data_arr = [int(i) for i in items]
                for i in range(len(data_arr)):
                    if i < 3:
                        data_arr[i] = normalise(data_arr[i], -2000, 2000)
                    elif i in range(3, 6):
                        data_arr[i] = normalise(data_arr[i], -250000, 250000)
                    elif i in range(6, 9):
                        data_arr[i] = normalise(data_arr[i], -2000, 2000)
                    elif i in range(9, 12):
                        data_arr[i] = normalise(data_arr[i], -250000, 250000)
                    elif i in range(12, 15):
                        data_arr[i] = normalise(data_arr[i], -2000, 2000)
                    elif i in range(15, 18):
                        data_arr[i] = normalise(data_arr[i], -250000, 250000)

                data_line.extend(data_arr)

                data_arr = data_line_raw['02']
                line = line[:-1]
                items = line.split(" ")
                print(data_arr)
                # data_arr = [int(i) for i in items]
                print(len(data_arr))
                for i in range(len(data_arr)):
                    if i < 3:
                        data_arr[i] = normalise(data_arr[i], -2000, 2000)
                    elif i in range(3, 6):
                        data_arr[i] = normalise(data_arr[i], -250000, 250000)
                    elif i in range(6, 9):
                        data_arr[i] = normalise(data_arr[i], -2000, 2000)
                    elif i in range(9, 12):
                        data_arr[i] = normalise(data_arr[i], -250000, 250000)
                    elif i in range(12, 15):
                        data_arr[i] = normalise(data_arr[i], -2000, 2000)
                    elif i in range(15, 18):
                        data_arr[i] = normalise(data_arr[i], -250000, 250000)

                data_line.extend(data_arr)

                data_arr = data_line_raw['03']
                line = line[:-1]
                items = line.split(" ")
                print(data_arr)
                # data_arr = [int(i) for i in items]
                print(len(data_arr))
                for i in range(len(data_arr)):
                    if i < 3:
                        data_arr[i] = normalise(data_arr[i], -2000, 2000)
                    elif i in range(3, 6):
                        data_arr[i] = normalise(data_arr[i], -250000, 250000)
                    elif i in range(6, 9):
                        data_arr[i] = normalise(data_arr[i], -2000, 2000)
                    elif i in range(9, 12):
                        data_arr[i] = normalise(data_arr[i], -250000, 250000)
                    elif i in range(12, 15):
                        data_arr[i] = normalise(data_arr[i], -2000, 2000)
                    elif i in range(15, 18):
                        data_arr[i] = normalise(data_arr[i], -250000, 250000)

                data_line.extend(data_arr)

                print(data_line)
                data.append(data_line)
            print(len(data))
            csv_file_path = os.path.join(PROJECT_DIR, 'data', 'processed', new_file_name)

            with open(csv_file_path, 'a', newline='') as out_file:
                csv_writer = csv.writer(out_file)
                csv_writer.writerows(data)
    else:
        continue
