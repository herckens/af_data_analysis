def find_key_of_dict(dic, val):
    """return the key of dictionary dic given the value"""
    return [k for k, v in dic.iteritems() if v == val][0]


def read_logfile(logfilename):
    """ Read a whole logfile. Take information from logfile header to see which
    column corresponds to which variable. Parameter logfilename is the full path to
    the logfile. Return a dictionary that contains for each variable a list with
    all values.
    A logfile looks like this:

    Column 0 time                                                                                                           
    Column 1 pos_x
    Column 2 pos_y
    Column 3 error
    Column 4 phase
    Column 5 count_rotations
    Column 6 time_for_last_rotation
    Column 7 is_catch_trial
    # I am a comment and I could be anywhere in the file.
    Type: baseline
    40935 0.655575 -157.484 0.0171131 -89.7615 0 0 0
    41012 0.655738 -157.48 0.01337 -89.7614 0 0 0
    41089 0.631434 -157.505 0.0386854 -89.7703 0 0 0
    ...

    The return would be a dictionary of this form:

    time: [40935, 41012, 41089]
    pos_x: [..., ..., ...]
    ...

    type is either "baseline", "training_with_feedback" or "training without feedback"
    """

    data = {}   # The return variable
    type = ""   # The second return variable
    column_map = {} # Will contain information to match a column to the
                    # corresponding variable:
                    # 0: 'time'
                    # 1: 'pos_x'
                    # 2: 'pos_y' ...

    logfile = open(logfilename,"r")
    lines = logfile.readlines()
    lines.pop() # delete the last line as it is typically incomplete
    for line in lines:                                                                                                      
        if (line.startswith('\n') or line.startswith('\r')):
            continue # we found an empty line
        # remove trailing newline ('\n') and split at spaces
        line = line.rstrip('\n')
        line = line.rstrip('\r')

        if line.startswith('#'): # found a comment
            print(line)
            continue

        words = line.split(" ")

        if (words[0] == "Type:"):
            type = words[1]
            continue # we're done with this line

        if (words[0] == "Column"):
            column_map[int(words[1])] = words[2]
            data[words[2]] = []
            continue # we're done with this line

        # Check whether we have an incomplete line and skip it
        if (len(words) < len(column_map)):
            print("WARNING: Found an incomplete line in logfile.")
            continue # we're done with this line

        # Skip all lines that are part of the 0th rotation
        if (column_map.values().count("count_rotations") > 0):
            if (words[find_key_of_dict(column_map, "count_rotations")] == "0"):
                continue # we're done with this line

        # Skip all lines that have a count_rotations that is too high
        if (column_map.values().count("count_rotations") > 0):
            if type == 'baseline':
                limit = 10
            elif type == 'training_with_feedback':
                limit = 100
            elif type == 'training_without_feedback':
                limit = 100
            if (int(words[find_key_of_dict(column_map, "count_rotations")]) > limit):
                continue # we're done with this line

        for i in column_map.keys():
            if (i >= len(words)):
                # if this is true, then we have an incomplete line, should be
                # ommitted.
                break
            data[column_map[i]].append(float(words[i]))

    return data, type
