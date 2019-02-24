import csv
import sys

def loadData():

    inputExp = (sys.argv[1]).split('-')[1]
    inputUser = (sys.argv[2]).split('-')[1]

    f1 = open('/Users/ithsirslawragga/PycharmProjects/dance-dance-software/HAPT Data Set/RawData/acc_exp' + inputExp + '_user' + inputUser + '.txt', 'r')
    f2 = open('/Users/ithsirslawragga/PycharmProjects/dance-dance-software/HAPT Data Set/RawData/gyro_exp' + inputExp + '_user' + inputUser + '.txt', 'r')
    f3 = open('/Users/ithsirslawragga/PycharmProjects/dance-dance-software/HAPT Data Set/RawData/labels.txt', 'r')

    lines1 = f1.readlines()
    lines2 = f2.readlines()
    lines3 = f3.readlines()
    mycsv = csv.writer(open('output.csv', 'w'))
    mycsv.writerow(['val1', 'val2', 'val3', 'val4', 'val5', 'val6', 'dance'])

    for line3 in lines3:
        labels = line3.split(" ")
        lower_count = int(labels[3])
        upper_count = int(labels[4].strip('\n'))
        if inputExp == labels[0].zfill(2) and inputUser == labels[1].zfill(2):
            count = 0
            for line1 in lines1:
                count += 1
                if lower_count <= count <= upper_count:
                    for line2 in lines2:
                        vals = line1.split(" ")
                        val1 = vals[0]
                        val2 = vals[1]
                        val3 = vals[2].strip('\n')
                        vals = line2.split(" ")
                        val4 = vals[0]
                        val5 = vals[1]
                        val6 = vals[2].strip('\n')
                        mycsv.writerow([val1, val2, val3, val4, val5, val6, labels[2]])
                        break