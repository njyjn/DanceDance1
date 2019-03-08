import os

label = {1: 'WALKING', 2: 'WALKING_UPSTAIRS', 3: 'WALKING_DOWNSTAIRS', 4: 'SITTING', 5: 'STANDING', 6: 'LAYING',
         7: 'STAND_TO_SIT', 8: 'SIT_TO_STAND', 9: 'SIT_TO_LIE', 10: 'LIE_TO_SIT', 11: 'STAND_TO_LIE', 12: 'LIE_TO_STAND'
         }

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
data_x_train_path = os.path.join(PROJECT_DIR, 'data', 'Train')
x_train_file = os.path.join(data_x_train_path, 'X_train.txt')
data_raw_path = os.path.join(PROJECT_DIR, 'data', 'raw')
label_file = os.path.join(data_raw_path, 'labels.txt')


with open(label_file, 'r') as in_file:
    stripped = (line.strip() for line in in_file)
    lines = (line.split(",") for line in stripped if line)
    for line in lines:
        items = line[0].split(" ")
        atts = []
        for item in items:
            att = int(item)
            atts.append(att)
        '''
        Column 1: experiment number ID, 
        Column 2: user number ID, 
        Column 3: activity number ID 
        Column 4: Label start point (in number of signal log samples (recorded at 50Hz))
        Column 5: Label end point (in number of signal log samples)
        '''
        expnum = atts[0]
        expnum_str = str(atts[0])
        if len(expnum_str) is 1:
            expnum_str = '0'+expnum_str
        userid = atts[1]
        userid_str = str(atts[1])
        if len(userid_str) is 1:
            userid_str = '0'+ userid_str
        activity = atts[2]
        start = atts[3]
        end = atts[4]
        acc_filename_to_extract = 'acc_' + 'exp' + expnum_str + '_user' + userid_str + '.txt'
        gyro_filename_to_extract = 'gyro_' + 'exp' + expnum_str + '_user' + userid_str + '.txt'
        print(acc_filename_to_extract)
        print(gyro_filename_to_extract)

        acc_filename_to_extract_path = os.path.join(data_raw_path, acc_filename_to_extract)
        gyro_filename_to_extract_path = os.path.join(data_raw_path, gyro_filename_to_extract)
        acc_readings = []
        gyro_readings = []

        with open(acc_filename_to_extract_path, 'r') as acc_file:
            stripped = (line.strip() for line in acc_file)
            lines = (line.split(",") for line in stripped if line)
            lines = list(lines)

            for reading in range(start, end):
                acc_readings.extend(lines[reading])

        with open(gyro_filename_to_extract_path, 'r') as gyro_file:
            stripped = (line.strip() for line in gyro_file)
            lines = (line.split(",") for line in stripped if line)
            lines = list(lines)

            for reading in range(start, end):
                gyro_readings.extend(lines[reading])

        readings_array = []
        for index in range(len(gyro_readings)):
            reading_line = acc_readings[index] + ' ' + gyro_readings[index]
            reading_att = reading_line.split(' ')
            reading = ''
            for read in reading_att:
                reading = reading + ',' + read
            reading = reading[1:]
            readings_array.append(reading)

        csv_filename = label[activity].lower() + userid_str + '.csv'
        csv_file_path = os.path.join(PROJECT_DIR, 'data', 'processed', csv_filename)

        with open(csv_file_path, 'a') as out_file:
            for line_to_write in readings_array:
                out_file.write(line_to_write)
                out_file.write('\n')
