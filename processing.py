import pylab
import numpy as np

def precondition_data(data):
    """
    Do some preconditioning of the data to make it more meaningful
    """
    length = len(data['pos_x'])

    # reverse direction of y axis to make plots align with table
    for i in range(0, length):
        data['pos_y'][i] = -data['pos_y'][i] 

    # take absolute value of every item in error
    for i in range(0, length):
        data['error'][i] = abs(data['error'][i])

    # multiply all is_catch_trial values by 10 to make them stand out in the plot
    for i in range(0, length):
        data['is_catch_trial'][i] = 10 * data['is_catch_trial'][i]

    # convert from milliseconds to seconds and shift time to begin at 0
    first_timestamp = data['time'][0]
    for i in range(0, length):
        data['time'][i] = (data['time'][i] - first_timestamp) / 1000.0

    # convert time_for_last_rotation from milliseconds to seconds
    for i in range(0, length):
        data['time_for_last_rotation'][i] = data['time_for_last_rotation'][i] / 1000.0

    return data


def calc_mean_error_per_n_rotations(error, phase, n):
    """ 
    Calculates for every time-step the mean error over the last n*360 degrees.
    The returned mean_error is a list of the same length as error.
    """
    # TODO Maybe there is a built-in hist() function?!?

    mean_error = []
    bins = []
    last_bins_index = 0
    rotation_iterator = 1 # takes values from 1 to n and then wraps back to 1

    # Get bins to be a list of length n*360
    for j in range(0, n*360):
        bins.append(0.0)

    # Save the first phase where trajectory starts. When we come back to this,
    # rotation_iterator has to be increased by one.
    first_bins_index = int(round(phase[0] % 360)) # convert phase from +-180 to [0,360]

    # Iterate over all error samples
    for i in range(0, len(error)):
        bins_index = int(round(phase[i]) % 360) # convert phase from +-180 to [0,360]
        if (last_bins_index != bins_index):
            bins[rotation_iterator * bins_index] = 0.0
            # If one rotation is completed, update rotation_iterator
            if (bins_index == first_bins_index):
                rotation_iterator += 1
                if rotation_iterator > n:
                    rotation_iterator = 1

        # find max error in this bin and store it in bins[]
        if (abs(error[i]) > bins[rotation_iterator * bins_index]):
            bins[rotation_iterator * bins_index] = abs(error[i])
        last_bins_index = bins_index

        # sum over all bins and normalize by number of bins
        sum = 0.0
        # for j in range(0, (n*360-1)):
        #     sum += bins[j]
        for item in bins:
            sum += item

        mean_error.append(sum / (n*360 - bins.count(0.0)))

    return mean_error


def moving_average(values, window_length):
    """
    Calculates for every time-step the average value over the last
    window_length samples. The returned smoothed_values is a list of
    the same length as values.
    Attention: This is very expensive for large number of values and large
    window_length.
    """
    #TODO use convolution with mean filter instead of moving average to get rid
    # of shift... peaks should stay at the point where they really happen. The
    # simple moving average washes them to the right.
    smoothed_values = []
    bins = []

    # get bins to be a list of length window_length, initialized with zeros
    for j in range(0, window_length):
        bins.append(0.0)

    bins_index = 0
    for sampleNo in range(0, len(values)):
        bins_index = bins_index % window_length # reset index to 0 if too big
        bins[bins_index] = abs(values[sampleNo])

        # take sum over all items in bins
        sum = 0.0
        for item in bins:
            sum += item

        # Divide sum by number of non-zero items that contributed to the sum
        smoothed_values.append(sum / (window_length - bins.count(0.0)))

    return smoothed_values


# def butterworth_filter(values, cutoff_freq = 20.0, dt = 0.002, order = 4):
#     """
#     Runs a digital butterworth lowpass filter over the values and returns the
#     filtered values as a list of the same length as the input.
# 
#     cutoff_freq is the desired cutoff frequency in Hz
#     dt is the sample time (time between two samples) in seconds
#     order is the order of the filter transfer function
#     """
#     import scipy.signal
#     # Get butterworth filter coefficients
#     b,a=scipy.signal.butter(order,(cutoff_freq * dt), btype='low', analog=0)
#     vals = np.array(values)
#     filtered_values = scipy.signal.filtfilt(b,a,vals)
#     return filtered_values


def calc_mean_circle(x_vals, y_vals):
    """
    For experiments without feedback.
    Find center by taking the mean over all data points. Compute mean radius.
    """
    sum_x = 0.0
    sum_y = 0.0
    length = len(x_vals)

    for i in range(0, length):
        sum_x += x_vals[i]
        sum_y += y_vals[i]

    mean_x = sum_x / length
    mean_y = sum_y / length

    # Find radius by taking the mean radius given the center that we already found
    sum_r = 0.0
    for i in range(0, length):
        sum_r += np.sqrt(x_vals[i] * x_vals[i] + y_vals[i] * y_vals[i])
    mean_radius = sum_r / length

    return mean_x, mean_y, mean_radius


def calc_mean_error(center_x, center_y, radius, x_vals, y_vals):
    """
    For experiments without feedback.
    Calculate the mean error over all rotations.
    """
    length = len(x_vals)
    sum = 0.0

    for i in range(0, length):
        x = x_vals[i] - center_x
        y = y_vals[i] - center_y
        sum += abs(radius - np.sqrt(x*x + y*y))

    return sum / length


def calc_error_samples(center_x, center_y, radius, x_vals, y_vals):
    """
    For experiments without feedback.
    Calculate the (signed, no abs()) error for each timestamp.
    Returns a list of lenth len(x_vals)
    """
    length = len(x_vals)
    errors = [] # will eventually contain the current error for each timestamp

    for i in range(0, length):
        x = x_vals[i] - center_x
        y = y_vals[i] - center_y
        error = np.sqrt(x*x + y*y) - radius 
        errors.append(error)

    return errors
