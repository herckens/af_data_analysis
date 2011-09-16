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

if logfiledir.endswith('_cg'):
    print('These plots are only valid for subjects in the WITH FEEDBACK group. The specified directory is of a control group subject. Exiting...')
    sys.exit()

fnames = os.listdir(logfiledir)                                                                                         
fnames.sort()

# get subject's name out of logfiledir, used for plot filenames
subjectName = logfiledir[42:len(logfiledir)-1]

for i in range(0, len(fnames)):
    fnames[i] = os.path.join(logfiledir, fnames[i])

for i in range(0, len(fnames)):
    print('Log file number ' + str(i))
    data, type, flags = read_logfile(fnames[i])    # read the logfile

    # Data Preconditioning
    data = processing.precondition_data(data)

    if (type != 'training_with_feedback'):
        continue

    else :
        print('Type = ' + type)

        # Set up the figure with all catch trials in one figure
        fig = pylab.figure(1)
        pylab.clf()
        pylab.axis('equal')
        pylab.xlabel('x [mm]')
        pylab.ylabel('y [mm]')
        pylab.title('Catch-Trial Trajectories')

        catchTrialPosX = []
        catchTrialPosY = []
        beforeCatchTrialPosX = []
        beforeCatchTrialPosY = []
        currRot = int(data['count_rotations'][0])
        lastRot = currRot
        lastIsCatchTrial = 0
        figureCounter = 1
        # loop over all samples in this logfile
        for sampleNo in range(0, len(data['pos_x'])):
            # determine the current rotation
            currRot = int(data['count_rotations'][sampleNo])
            # have we just completed a rotation?
            if currRot != lastRot:
                # is the new rotation a catch trial or not?
                if (data['is_catch_trial'][sampleNo] != 0):
                    # empty the catch trial position vectors
                    catchTrialPosX = []
                    catchTrialPosY = []
                else : # not a catch trial
                    # check if last trial was a catch trial
                    if (lastIsCatchTrial != 0):
                        # yes, last trial was a catch trial, the one before
                        # that was not, so now we can plot the two
                        figureCounter += 1
                        fig = pylab.figure(figureCounter)
                        pylab.clf()
                        pylab.plot(beforeCatchTrialPosX, beforeCatchTrialPosY, label = 'Before', c='b')
                        pylab.plot(catchTrialPosX, catchTrialPosY, label = 'Catch-Trial', c='g')
                        pylab.axis('equal')
                        pylab.xlabel('x [mm]')
                        pylab.ylabel('y [mm]')
                        pylab.title('Catch-Trial # ' + str(figureCounter-1))
                        ### plot circles ###
                        ax = fig.add_subplot(111)
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
                        pylab.savefig('plotCatchTrial_' + subjectName + '_No' + str(figureCounter-1) + '.pdf')

                        fig = pylab.figure(1)
                        if (figureCounter < 9):
                            pylab.plot(catchTrialPosX, catchTrialPosY, '-', label = str(figureCounter-1))
                        else :
                            pylab.plot(catchTrialPosX, catchTrialPosY, '--', label = str(figureCounter-1))

                    # empty the before catch trial position vectors
                    beforeCatchTrialPosX = []
                    beforeCatchTrialPosY = []

                lastRot = currRot
            # is the current rotation a catch trial or not?
            if (data['is_catch_trial'][sampleNo] != 0):
                catchTrialPosX.append(data['pos_x'][sampleNo])
                catchTrialPosY.append(data['pos_y'][sampleNo])
                lastIsCatchTrial = 1
            else :
                beforeCatchTrialPosX.append(data['pos_x'][sampleNo])
                beforeCatchTrialPosY.append(data['pos_y'][sampleNo])
                lastIsCatchTrial = 0

fig = pylab.figure(1)
### plot circles ###
ax = fig.add_subplot(111)
# desired trajectory
circle = pylab.Circle((0, 0), radius = 130.0, fill = False, color = 'r')#, label = 'Desired')
ax.add_patch(circle)
# deadband outer
circle = pylab.Circle((0, 0), radius = 134.0, fill = False, color = 'k')#, label = 'Deadband')
ax.add_patch(circle)
# deadband inner
circle = pylab.Circle((0, 0), radius = 126.0, fill = False, color = 'k')
ax.add_patch(circle)
# saturation outer
circle = pylab.Circle((0, 0), radius = 230.0, fill = False, color = 'm')#, label = 'Saturation')
ax.add_patch(circle)
pylab.legend()
pylab.savefig('plotCatchTrial_' + subjectName + '_allCatchTrials.pdf')

# pylab.show()    # actually show all the plots. This should be at the bottom.

#raw_input('Press enter to exit')

