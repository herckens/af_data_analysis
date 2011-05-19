import pylab
import numpy as np
import os

import sys

from read_logfile import *



if len(sys.argv) < 2:
    print 'Please specify a directory that contains several subfolders with subject logfiles'
    sys.exit()
subjectdir = sys.argv[1]
