import pylab
import numpy as np
import os
import sys
import scipy.signal

from read_logfile import *
import processing


if len(sys.argv) < 2:
    print 'Please specify a directory that contains several subfolders with subject logfiles'
    sys.exit()
subjectDir = sys.argv[1]
logFileDirs = os.listdir(subjectDir)

scriptDir = os.getcwd() # save current dir to go back to it later

speedsNormal = [] # contains as many items as there are normal subjects
speedsCtrlGrp = [] # contains as many items as there are control group subjects
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
        speedsCtrlGrp.append([]) # will contain one value per timestamp
    else:
        isCtrlGrp = False
        countNormal += 1
        speedsNormal.append([]) # will contain one value per timestamp

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

        # rotOffset = 0 # Baseline
        # if i == 1:
        #     rotOffset = 10 # Training
        # elif i == 2:
        #     rotOffset = 110 # Retention

        counter = 0                         # counts samples per rotation
        lastX = data['pos_x'][0]
        lastY = data['pos_y'][0]
        lastTime = data['time'][0]-0.0001 # has to be different, to prevent division by 0 later
        # loop over all samples in this logfile
        for sampleNo in range(0, length):
            x = data['pos_x'][sampleNo]
            y = data['pos_y'][sampleNo]
            time = data['time'][sampleNo]
            deltaT = time - lastTime
            # if deltaT > 0.04:
                # print('==============')
                # print(deltaT)
                # print(lastTime)
                # print(time)
            if isCtrlGrp:
                speedsCtrlGrp[countCtrlGrp-1].append(np.sqrt((x-lastX)**2 + (y-lastY)**2) / deltaT)
            else :
                speedsNormal[countNormal-1].append(np.sqrt((x-lastX)**2 + (y-lastY)**2) / deltaT)
            lastX = x
            lastY = y
            lastTime = time

        fig = pylab.figure(1)
        if isCtrlGrp:
            pylab.plot(data['time'], speedsCtrlGrp[countCtrlGrp-1], c='k', linestyle = '--', label='without feedback')
            speedsCtrlGrp[countCtrlGrp-1] = []
        else :
            # Get butterworth filter coefficients. 20 Hz cutoff. 0.002 is a typical delta T
            b,a=scipy.signal.butter(4,(20.0*0.002),btype='low',analog=0)
            speedsNormal[countNormal-1][0] = 60.0
            vals = np.array(speedsNormal[countNormal-1])
            print(vals)
            speeds = scipy.signal.filtfilt(b,a,vals)
            print(speeds)
            pylab.plot(data['time'], speeds, c='k', linestyle='-', label='with feedback')
            # pylab.plot(data['time'], speedsNormal[countNormal-1], c='k', linestyle = '-', label='with feedback')
            speedsNormal[countNormal-1] = []
        pylab.show()
        # end of logfile

    os.chdir(scriptDir)
    # end of subject

# fig = pylab.figure(1)
# pylab.clf()
# for i in range(0,countNormal):
#     pylab.plot(range(1,len(meansNormal['velError'])+1), meansNormal['velError'], c='k', linestyle = '-', label='timing error (With Feedback)')
# for i in range(0,countCtrlGrp):
#     pylab.plot(range(1,len(meansCtrlGrp['velError'])+1), meansCtrlGrp['velError'], c='k', linestyle = '--', label='timing error (Control Group)')
# pylab.xlabel('Trials')
# pylab.ylabel('mean |timing error| [s]')
# pylab.title('|timing error| per trial, average over all subjects')
# pylab.legend()
# pylab.savefig('plot3.svg')

# from matplotlib.backends.backend_pdf import PdfPages
# pp = PdfPages('plot3.pdf')
# pp.savefig()
# pp.close()

#pylab.show()    # actually show all the plots. This should be at the bottom.

