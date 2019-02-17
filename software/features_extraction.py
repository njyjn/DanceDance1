import numpy as np
import pandas as pd


# features extraction

def minimum(window):
    # minimum of each axis
    minimums = []
    for i in range(6):
        minimums.append(np.min(window[:, i]))
    return minimums


def maximum(window):
    # maximum of each axis
    maximums = []
    for i in range(6):
        maximums.append(np.max(window[:, i]))
    return maximums


def std_dev(window):
    # std of each axis
    std_dev = []
    for i in range(6):
        std_dev.append(np.std(window[:, i]))
    return std_dev


def mean(window):
    # mean of each axis
    mean = []
    for i in range(6):
        mean.append(np.mean(window[:, i]))
    return mean

# def corr_coeff(window):
#     # correlation btw accel and gyro
#     coeff = []
#     #     coeff.append(np.corrcoef(window[:,6], window[:,7])[0][1])
#     #     coeff.append(np.corrcoef(window[:,6], window[:,8])[0][1])
#     #     coeff.append(np.corrcoef(window[:,7], window[:,8])[0][1])
#     #     coeff.append(np.corrcoef(window[:,9], window[:,10])[0][1])
#     #     coeff.append(np.corrcoef(window[:,9], window[:,11])[0][1])
#     #     coeff.append(np.corrcoef(window[:,10], window[:,11])[0][1])
#
#     coeff.append(np.corrcoef(window[:, 0], window[:, 6])[0][1])
#     coeff.append(np.corrcoef(window[:, 2], window[:, 8])[0][1])
#     coeff.append(np.corrcoef(window[:, 4], window[:, 10])[0][1])
#     return coeff


def extract_features(window):
    features = []
    features.extend(mean(window))
    features.extend(minimum(window))
    features.extend(maximum(window))
    features.extend(std_dev(window))
    return features
