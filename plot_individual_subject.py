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

# get subject's name out of logfiledir, used for plot filenames
subjectName = logfiledir[42:len(logfiledir)-1]

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
            realType = 'PostAssessment'
        elif ((i != 0) and (i != 2)):
            print('Cannot determine wether this is Baseline or PostAssessment. Weird number of files.')
            realType = 'Unknown'

        print('Type = ' + realType)

        #######################
        ### Plot trajectory ###
        #######################

        figureCounter += 1
        fig = pylab.figure(figureCounter)
        pylab.plot(data['pos_x'], data['pos_y'], label= 'Trajectory')
        pylab.axis('equal')
        pylab.xlabel('x [mm]')
        pylab.ylabel('y [mm]')
        pylab.title(realType + ' Trajectory')
        pylab.legend()

        ##########################################################################
        ### Find center and radius of circle during baseline and after effects ###
        ##########################################################################

        center_x, center_y, radius = processing.calc_mean_circle(data['pos_x'], data['pos_y'])
        print("Mean Radius = " + str(radius))
        error = processing.calc_mean_error(center_x, center_y, radius, data['pos_x'], data['pos_y'])

        if (realType == 'Baseline'):
            meanErrorBaseline = error
        elif (realType == 'PostAssessment'):
            meanErrorRetention = error

        fig = pylab.figure(figureCounter)
        pylab.plot(center_x, center_y, 'o', label='Center')
        pylab.plot(0, 0, 'o', label='Origin')

        # Plot the average circle
        ax = fig.add_subplot(111)
        circle = pylab.Circle((center_x, center_y), radius = radius, fill = False, color = 'r', label = 'Average')
        ax.add_patch(circle)

        # Plot the desired circle
        circle = pylab.Circle((0.0, 0.0), radius = radius, fill = False, color = 'r', ls = 'dashed', label = 'Desired')
        ax.add_patch(circle)

        pylab.legend()
        pylab.savefig('plotTraj' + realType + '_' + subjectName + '.svg')


    elif (type == 'training_with_feedback'):
        print('Type = ' + type)

        ################################
        ### Plot mean error vs. time ###
        ################################

        # mean_error_per_rot = processing.calc_mean_error_per_n_rotations(data['error'], data['phase'], 5)
        # # mean_error_per_rot = processing.butterworth_filter(data['error'], 0.9, 0.002, 4)

        # figureCounter += 1
        # fig = pylab.figure(figureCounter)
        # pylab.clf()
        # pylab.plot(data['time'], mean_error_per_rot, label='mean error per rotation')
        # pylab.plot(data['time'], data['time_for_last_rotation'], label='time for previous rotation')
        # pylab.plot(data['time'], data['is_catch_trial'], label='is catch trial')
        # pylab.xlabel('time [s]')
        # pylab.ylabel('mean error [mm]')
        # pylab.legend()

        #############################################
        ### Plot moving average of error vs. time ###
        #############################################

        # moving_averaged_error = processing.moving_average(data['error'], 1000)

        # figureCounter += 1
        # fig = pylab.figure(figureCounter)
        # pylab.clf()
        # pylab.plot(data['time'], moving_averaged_error, label='moving average of error')
        # pylab.plot(data['time'], data['time_for_last_rotation'], label='time for previous rotation')
        # pylab.plot(data['time'], data['is_catch_trial'], label='is catch trial')
        # pylab.xlabel('time [s]')
        # pylab.ylabel('moving average of error [mm]')
        # pylab.legend()

        #######################
        ### Plot trajectory ###
        #######################

        figureCounter += 1
        fig = pylab.figure(figureCounter)

        # plot trajectory
        ax = fig.add_subplot(111)
        pylab.plot(data['pos_x'], data['pos_y'], label = 'Trajectory')
        pylab.axis('equal')
        pylab.xlabel('x [mm]')
        pylab.ylabel('y [mm]')
        pylab.title(type + ' Trajectory')

        # plot circles:
        #ax = fig.add_subplot(111)
        # desired trajectory
        circle = pylab.Circle((0, 0), radius = 130.0, fill = False, color = 'r', label = 'Desired')
        ax.add_patch(circle)
        # deadband outer
        circle = pylab.Circle((0, 0), radius = 134.0, fill = False, color = 'k', label = 'Deadband')
        ax.add_patch(circle)
        # deadband inner
        circle = pylab.Circle((0, 0), radius = 126.0, fill = False, color = 'k')
        ax.add_patch(circle)
        # saturation outer
        circle = pylab.Circle((0, 0), radius = 230.0, fill = False, color = 'm', label = 'Saturation')
        ax.add_patch(circle)
        pylab.legend()
        pylab.savefig('plotTraj' + 'TrainingWithFeedback_' + subjectName + '.svg')

    elif (type == 'training_without_feedback'):
        print('Type = ' + type)

        #######################
        ### Plot trajectory ###
        #######################

        figureCounter += 1
        fig = pylab.figure(figureCounter)
        pylab.plot(data['pos_x'], data['pos_y'], label = 'Trajectory')
        pylab.axis('equal')
        pylab.xlabel('x [mm]')
        pylab.ylabel('y [mm]')
        pylab.title(type + ' Trajectory')
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

        # Plot the desired circle
        circle = pylab.Circle((0.0, 0.0), radius = 130.0, fill = False, color = 'r', ls = 'dashed', label = 'Desired')
        ax.add_patch(circle)

        pylab.legend()
        pylab.savefig('plotTraj' + 'TrainingWithoutFeedback_' + subjectName + '.svg')

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
print('Mean error during post-assessment = ' + str(meanErrorRetention))
improvement = 100 - meanErrorRetention / meanErrorBaseline * 100.0
print('Improvement = ' + str(int(improvement)) + ' %')



# pylab.show()    # actually show all the plots. This should be at the bottom.

#raw_input('Press enter to exit')
