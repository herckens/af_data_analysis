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

meanErrorNormal = [] # contains as many items as there are normal subjects
meanErrorCtrlGrp = [] # contains as many items as there are control group subjects
countNormal = 0
countCtrlGrp = 0
for subjectNo in range(0, len(logFileDirs)):
    if (logFileDirs[subjectNo].startswith('.')):
        # some hidden folder. surely doesn't contain logfiles
        continue
    # Check whether this subject was in control group or not
    if (logFileDirs[subjectNo].endswith('_cg')):
        isCtrlGrp = True
        countCtrlGrp += 1
        meanErrorCtrlGrp.append([]) # will contain three means (baseline, training, retention)
    else :
        isCtrlGrp = False
        countNormal += 1
        meanErrorNormal.append([]) # will contain three means (baseline, training, retention)

    # Go into directory
    os.chdir(os.path.join(subjectDir, logFileDirs[subjectNo]))
    fnames = os.listdir('.') # all files in directory
    fnames.sort()

    if (len(fnames) != 3):
        print('WARNING: There should be 3 logfiles but I found ' + str(len(fnames)))
        print('in ' + subjectDir + '/' + logFileDirs[subjectNo])

    for fileNo in range(0, len(fnames)):
        print('Log file number ' + str(fileNo))
        data, type = read_logfile(fnames[fileNo])    # read the logfile

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

        # loop over all samples in this logfile
        sum = 0.0
        for sampleNo in range(0, length):
            sum += data['error'][sampleNo]

        if isCtrlGrp:
            meanErrorCtrlGrp[countCtrlGrp-1].append(sum) # deleted division: / float(length)
        else :
            meanErrorNormal[countNormal-1].append(sum) # deleted division: / float(length)

    os.chdir(scriptDir)
    # end of subject


### Write data to new txt file for statistical analysis ###
f = open('plot6bNoDivide_data.txt', 'w')
f.write('# <subjectNumber> <meanErrorBaseline> <meanErrorRetention>\n')
f.write('### Normal Subjects ###\n')
for subjectNo in range(0, len(meanErrorNormal)):
    f.write(str(subjectNo) + ' ' + str(meanErrorNormal[subjectNo][0]) + ' ' +
            str(meanErrorNormal[subjectNo][2]) + '\n')
f.write('### Control Group Subjects ###\n')
for subjectNo in range(0, len(meanErrorCtrlGrp)):
    f.write(str(subjectNo) + ' ' + str(meanErrorCtrlGrp[subjectNo][0]) + ' ' +
            str(meanErrorCtrlGrp[subjectNo][2]) + '\n')
f.close()



### Print with training ###
fig = pylab.figure(1)
pylab.clf()
# expPhase = ['Baseline', 'Training', 'Retention']
expPhase = [1, 2, 3]
for subjectNo in range(0, len(meanErrorNormal)):
    pylab.plot(expPhase, meanErrorNormal[subjectNo], '*-', c='k', label='With Feedback')
for subjectNo in range(0, len(meanErrorCtrlGrp)):
    pylab.plot(expPhase, meanErrorCtrlGrp[subjectNo], 'o--', c='k', label='Without Feedback')
pylab.xlabel('Experiment Phase')
pylab.ylabel('sum |error| [mm]')
pylab.title('Sum |error|')
pylab.legend()
pylab.savefig('plot6aNoDivide.svg')

### Print without training ###
fig = pylab.figure(1)
pylab.clf()
# expPhase = ['Baseline', 'Training', 'Retention']
expPhase = [1, 2]
for subjectNo in range(0, len(meanErrorNormal)):
    pylab.plot(expPhase, [meanErrorNormal[subjectNo][0], meanErrorNormal[subjectNo][2]], '*-', c='k', label='With Feedback')
for subjectNo in range(0, len(meanErrorCtrlGrp)):
    pylab.plot(expPhase, [meanErrorCtrlGrp[subjectNo][0], meanErrorCtrlGrp[subjectNo][2]], 'o--', c='k', label='Without Feedback')
pylab.xlabel('Experiment Phase')
pylab.ylabel('Sum |error| [mm]')
pylab.title('Sum |error|')
pylab.legend()
pylab.axis([0.9, 2.1, 5, 1100000])
pylab.savefig('plot6bNoDivide.svg')

# from matplotlib.backends.backend_pdf import PdfPages
# pp = PdfPages('plot6.pdf')
# pp.savefig()
# pp.close()

#pylab.show()    # actually show all the plots. This should be at the bottom.

