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


def calc_mean_error_per_rotation(time, error, phase):
    """ 
    Calculates for every time-step the mean error over the last 360 degrees.
    The returned mean_error is a list of the same length as time.
    """
    # TODO Maybe it is better to average over time, not over degrees? Will give
    # different result if subject stays at one positon (phase) with some error
    # for longer period of time...
    # TODO Maybe there is a built-in hist() function?!?

    mean_error = []
    bins = []
    last_phase = 0.0
    last_bins_index = 0

    # Get bins to be a list of length 360
    for j in range(0,360):
        bins.append(0.0)

    # Iterate over all time steps
    for i in range(0, len(time)):
        bins_index = int(round(phase[i]) % 360) # convert from +-180 to [0,360]
        if (last_bins_index != bins_index):
            bins[bins_index] = 0.0
        # find max error in this bin and store it in bins[]
        if (abs(error[i]) > bins[bins_index]):
            bins[bins_index] = abs(error[i])
        last_bins_index = bins_index

        # sum over all bins and normalize by number of bins
        sum = 0
        for j in range(0,359):
            sum += bins[j]

        mean_error.append(sum / 360)

    return mean_error


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
