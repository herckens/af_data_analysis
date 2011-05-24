import pylab
import numpy as np
import os

import sys

from read_logfile import *
import processing

#TODO try filtering the output before plotting

desiredTimePerRot = 9.0 # in [s], the optimal time a subject would need for one rotation

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
meansNormal['velError'] = 120 * [0.0]  # initialize with 120 zeros
meansCtrlGrp['velError'] = 120 * [0.0]  # initialize with 120 zeros
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

        length = len(data['pos_x'])

        # Precondition the data
        data = processing.precondition_data(data)

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
            # TODO maybe without the abs() in next line?!
            meanErrPerRot[rotOffset+int(data['count_rotations'][sampleNo])-1] += abs(data['time_for_last_rotation'][sampleNo] - desiredTimePerRot)
            # meanErrPerRot[rotOffset+int(data['count_rotations'][sampleNo])-1] += data['time_for_last_rotation'][sampleNo] - desiredTimePerRot
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
            meansCtrlGrp['velError'][rotNo] += meanErrPerRot[rotNo]
        else :
            meansNormal['velError'][rotNo] += meanErrPerRot[rotNo]

    os.chdir(scriptDir)
    # end of subject

for rotNo in range(0, len(meansNormal['velError'])):
    meansNormal['velError'][rotNo] = meansNormal['velError'][rotNo] / countNormal
    meansCtrlGrp['velError'][rotNo] = meansCtrlGrp['velError'][rotNo] / countCtrlGrp

fig = pylab.figure(1)
pylab.clf()
pylab.plot(range(1,len(meansNormal['velError'])+1), meansNormal['velError'], c='k', linestyle = '-', label='timing error (With Feedback)')
pylab.plot(range(1,len(meansCtrlGrp['velError'])+1), meansCtrlGrp['velError'], c='k', linestyle = '--', label='timing error (Control Group)')
pylab.xlabel('Trials')
pylab.ylabel('mean |timing error| [s]')
pylab.title('|timing error| per trial, average over all subjects')
pylab.legend()
pylab.savefig('plot3.svg')

# from matplotlib.backends.backend_pdf import PdfPages
# pp = PdfPages('plot3.pdf')
# pp.savefig()
# pp.close()

#pylab.show()    # actually show all the plots. This should be at the bottom.
