import pylab
import os

import sys

from read_logfile import *
import processing # contains functions to process auditory feedback log data


# Some global variables
meanErrorBaseline = 0.0
meanErrorRetention = 0.0
figureCounter = 0

if len(sys.argv) < 2:
    print 'Please specify a logfile directory'
    sys.exit()
logfiledir = sys.argv[1]

fnames = os.listdir(logfiledir)                                                                                         
fnames.sort()

for i in range(0, len(fnames)):
    fnames[i] = os.path.join(logfiledir, fnames[i])

for i in range(0, len(fnames)):
    print('Log file number ' + str(i))
    data, type = read_logfile(fnames[i])    # read the logfile

    ############################
    ### Data Preconditioning ###
    ############################

    data = processing.precondition_data(data)

    if (type == 'baseline'):
        realType = 'Unknown'
        if (i == 0):
            realType = 'Baseline'
        elif (i > 1):
            realType = 'Retention'
        elif ((i != 0) and (i != 2)):
            print('Cannot determine wether this is Baseline or Retention. Weird number of files.')
            realType = 'Unknown'

        print('Type = ' + realType)

        #######################
        ### Plot trajectory ###
        #######################

        figureCounter += 1
        fig = pylab.figure(figureCounter)
        pylab.plot(data['pos_x'], data['pos_y'], label= realType + ' Trajectory')
        pylab.axis('equal')
        pylab.xlabel('x [mm]')
        pylab.ylabel('y [mm]')
        pylab.legend()

        ##########################################################################
        ### Find center and radius of circle during baseline and after effects ###
        ##########################################################################

        center_x, center_y, radius = processing.calc_mean_circle(data['pos_x'], data['pos_y'])
        print("Mean Radius = " + str(radius))
        error = processing.calc_mean_error(center_x, center_y, radius, data['pos_x'], data['pos_y'])

        if (realType == 'Baseline'):
            meanErrorBaseline = error
        elif (realType == 'Retention'):
            meanErrorRetention = error

        fig = pylab.figure(figureCounter)
        pylab.plot(center_x, center_y, 'o', label='Center')
        pylab.plot(0, 0, 'o', label='Origin')

        # Plot the average circle
        ax = fig.add_subplot(111)
        circle = pylab.Circle((center_x, center_y), radius = radius, fill = False, color = 'r')
        ax.add_patch(circle)

        pylab.legend()


    elif (type == 'training_with_feedback'):
        print('Type = ' + type)

        ################################
        ### Plot mean error vs. time ###
        ################################

        mean_error_per_rot = processing.calc_mean_error_per_rotation(data['time'], data['error'], data['phase'])

        figureCounter += 1
        fig = pylab.figure(figureCounter)
        pylab.clf()
        pylab.plot(data['time'], mean_error_per_rot, label='mean error per rotation')
        pylab.plot(data['time'], data['time_for_last_rotation'], label='time for previous rotation')
        pylab.plot(data['time'], data['is_catch_trial'], label='is catch trial')
        pylab.xlabel('time [s]')
        pylab.ylabel('mean error [mm]')
        pylab.legend()

        #####################
        ### Plot position ###
        #####################

        figureCounter += 1
        fig = pylab.figure(figureCounter)
        pylab.plot(data['pos_x'], data['pos_y'], label = type + ' Trajectory')
        pylab.axis('equal')
        pylab.xlabel('x [mm]')
        pylab.ylabel('y [mm]')
        pylab.legend()

    elif (type == 'training_without_feedback'):
        print('Type = ' + type)

        #######################
        ### Plot trajectory ###
        #######################

        figureCounter += 1
        fig = pylab.figure(figureCounter)
        pylab.plot(data['pos_x'], data['pos_y'], label= type + ' Trajectory')
        pylab.axis('equal')
        pylab.xlabel('x [mm]')
        pylab.ylabel('y [mm]')
        pylab.legend()

        ########################################
        ### Find center and radius of circle ###
        ########################################

        center_x, center_y, radius = processing.calc_mean_circle(data['pos_x'], data['pos_y'])
        print("Mean Radius = " + str(radius))
        error = processing.calc_mean_error(center_x, center_y, radius, data['pos_x'], data['pos_y'])

        pylab.figure(figureCounter)
        pylab.plot(center_x, center_y, 'o', label='Center')
        pylab.plot(0, 0, 'o', label='Origin')

        # Plot the average circle
        ax = fig.add_subplot(111)
        circle = pylab.Circle((center_x, center_y), radius = radius, fill = False, color = 'r')
        ax.add_patch(circle)

        pylab.legend()

    else :
        print('Unknown type of log file. Please check the following file')
        print(fnames[i])




    ###########################
    ### Plot error vs. time ###
    ###########################

    # pylab.figure(2)
    # pylab.plot(data['time'], data['error'], label='error')
    # pylab.plot(data['time'], data['time_for_last_rotation'], label='time for previous rotation')
    # pylab.plot(data['time'], data['is_catch_trial'], label='is catch trial')
    # pylab.xlabel('time [s]')
    # pylab.ylabel('error [mm]')
    # pylab.legend()
    # 



#############################
### Calculate improvement ###
#############################

print('Mean error during baseline = ' + str(meanErrorBaseline))
print('Mean error during retention = ' + str(meanErrorRetention))
improvement = 100 - meanErrorRetention / meanErrorBaseline * 100.0
print('Improvement = ' + str(int(improvement)) + ' %')



pylab.show()    # actually show all the plots. This should be at the bottom.

#raw_input('Press enter to exit')
