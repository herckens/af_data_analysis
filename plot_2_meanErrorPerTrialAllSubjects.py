import pylab
import numpy as np
import os

import sys

from read_logfile import *
import processing



if len(sys.argv) < 2:
    print 'Please specify a directory that contains several subfolders with subject logfiles'
    sys.exit()
subjectDir = sys.argv[1]
logFileDirs = os.listdir(subjectDir)

scriptDir = os.getcwd() # save current dir to go back to it later

meansNormal = {}
meansCtrlGrp = {}
countNormal = 0
countCtrlGrp = 0
meansNormal['error'] = 120 * [0.0]  # initialize with 120 zeros
meansCtrlGrp['error'] = 120 * [0.0]  # initialize with 120 zeros
for subjectNo in range(0, len(logFileDirs)):
    if (logFileDirs[subjectNo].startswith('.')):
        # some hidden folder. surely doesn't contain logfiles
        continue
    # Check whether this subject was in control group or not
    if (logFileDirs[subjectNo].endswith('_cg')):
        isCtrlGrp = True
        countCtrlGrp += 1
    else:
        isCtrlGrp = False
        countNormal += 1

    # Go into directory
    os.chdir(os.path.join(subjectDir, logFileDirs[subjectNo]))
    fnames = os.listdir('.') # all files in directory
    fnames.sort()

    if (len(fnames) != 3):
        print('WARNING: There should be 3 logfiles but I found ' + str(len(fnames)))
        print('in ' + subjectDir + '/' + logFileDirs[subjectNo])

    for i in range(0, len(fnames)):
        print('Log file number ' + str(i))
        data, type = read_logfile(fnames[i])    # read the logfile

        # if no feedback, compute error from dynamically calculated center and
        # radius, because subject might have been drawing circles not around
        # the origin but any other point in the table plane, so the logged
        # error variable is useless.
        if (type == 'baseline' or type == 'training_without_feedback'):
            center_x, center_y, radius = processing.calc_mean_circle(data['pos_x'], data['pos_y'])
            data['error'] = processing.calc_error_samples(center_x, center_y, radius, data['pos_x'], data['pos_y'])

        length = len(data['error'])

        # Precondition the data
        data = processing.precondition_data(data)

        if (type == 'training_with_feedback'):
            data['error'] = processing.calc_mean_error_per_n_rotations(data['error'], data['phase'], 5)

        rotOffset = 0 # Baseline
        if i == 1:
            rotOffset = 10 # Training
        elif i == 2:
            rotOffset = 110 # Retention

        if i == 0:
            meanErrPerRot = 120 * [0.0]     # initialize with 120 zeros
        currRot = int(data['count_rotations'][0])
        lastRot = currRot                   # needed to reset counter
        counter = 0                         # counts samples per rotation
        # loop over all samples in this logfile
        for sampleNo in range(0, length):
            # determine the current rotation
            currRot = int(data['count_rotations'][sampleNo])
            # update the sum for the current rotation
            meanErrPerRot[rotOffset+int(data['count_rotations'][sampleNo])-1] += data['error'][sampleNo]
            if currRot != lastRot:
                # compute average for the just completed rotation
                meanErrPerRot[rotOffset+lastRot-1] = meanErrPerRot[rotOffset+lastRot-1] / counter
                counter = 0
                lastRot = currRot
            counter += 1
        # compute average for the last completed rotation (actually the last in
        # this logfile).
        meanErrPerRot[rotOffset+lastRot-1] = meanErrPerRot[rotOffset+lastRot-1] / counter
        counter = 0
        # end of logfile

    print(meanErrPerRot)
    for rotNo in range(0, len(meanErrPerRot)):
        if isCtrlGrp:
            meansCtrlGrp['error'][rotNo] += meanErrPerRot[rotNo]
        else :
            meansNormal['error'][rotNo] += meanErrPerRot[rotNo]

    os.chdir(scriptDir)
    # end of subject

for rotNo in range(0, len(meansNormal['error'])):
    meansNormal['error'][rotNo] = meansNormal['error'][rotNo] / countNormal
    meansCtrlGrp['error'][rotNo] = meansCtrlGrp['error'][rotNo] / countCtrlGrp

fig = pylab.figure(1)
pylab.clf()
pylab.plot(range(1,len(meansNormal['error'])+1), meansNormal['error'], c='k', linestyle = '-', label='error (With Feedback)')
# pylab.plot(range(1,len(meansNormal['error'])+1), meansNormal['error'], 'o', c='k')
pylab.plot(range(1,len(meansCtrlGrp['error'])+1), meansCtrlGrp['error'], c='k', linestyle = '--', label='error (Control Group)')
# pylab.plot(range(1,len(meansCtrlGrp['error'])+1), meansCtrlGrp['error'], '*', c='k')
pylab.xlabel('Trials')
pylab.ylabel('mean |error| [mm]')
pylab.title('Mean |error| per trial, average over all subjects')
pylab.legend()
pylab.savefig('plot2.svg')

# from matplotlib.backends.backend_pdf import PdfPages
# pp = PdfPages('plot2.pdf')
# pp.savefig()
# pp.close()

#pylab.show()    # actually show all the plots. This should be at the bottom.
