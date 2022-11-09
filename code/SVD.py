# edit file path
REF = 'ref_01.txt'
READ = 'read_01.txt'
DEBUG_MODE = True # True/False

with open(REF) as f:
    ref = f.read().splitlines()[0]
with open(READ) as f:
    reads = f.read().splitlines()
if (DEBUG_MODE):
    print(ref)

def get_score(read, ref_part):
    # calculate score for 1 read and 1 position of ref 
    score = 0
    for i in range(len(ref_part)):
        if read[i] == ref_part[i]:
            score += 1
    return score

def read_mapping(read, ref):
    # perform read_mapping for 1 read
    max_score, best_idx = (-1, -1)
    for i in range(len(ref) - len(read) + 1):
        score = get_score(read, ref[i:i+len(read)])
        if score > max_score:
            max_score = score
            best_idx = i
        if max_score >= 0.8*len(read):
            # max_score good enough
            return (max_score, best_idx)
    return (max_score, best_idx)

def get_percent_match(read, ref_part, is_read_inv):
    if (is_read_inv):
        read = read[::-1]
    percent = 0
    for i in range(len(read)):
        if read[i] == ref_part[i]:
            percent += 1
    return percent/len(read)

def get_breakpoint_index(read, ref_part, is_R_type):
    # ref:  AAAAAAA
    # read: AAABBBB
    #          ^
    # index = 3
    if (is_R_type):
        for i in range(len(read)):
            if read[i] != ref_part[i]:
                return i
    else:
        for i in range(len(read)-1,-1,-1):
            if read[i] != ref_part[i]:
                return i

def get_mapping_type(read1, read1_idx, is_read1_inv, read2, read2_idx, is_read2_inv, normal_space, ref):
    '''
    definition:
    read1 = [    >
    read1 reverse = [  r >
    read2 = <    ]
    read2 reverse = <  r ]
    normal distance between read1 and read2 = ---
    short distance between read1 and read2 = -
    long distance between read1 and read2 = ------
    mapped = <    ]
    soft-clipped = <  ##]
    unmapped = <####]

    type:
    B  = <    ]-?-[    > 
    I  = [  r >-?-<  r ] || [    >-?-<  r ] || [  r >-?-<   ]
    S  = [    >-<    ]
    L  = [    >------<    ]
    M  = [    >---<    ]
    R1 = [    >---<  ##]
    R2 = [    >---<####]
    L1 = [##  >---<    ]
    L2 = [####>---<    ]
    U  = [####>---<####]
    '''
    p1 = get_percent_match(read1,ref[read1_idx:read1_idx+len(read1)],is_read1_inv)
    p2 = get_percent_match(read2,ref[read2_idx:read2_idx+len(read2)],is_read2_inv)
    MAPPED_THRESHOLD = 0.85
    UNMAPPED_THRESHOLD = 0.6

    if (p1 >= UNMAPPED_THRESHOLD or p2 >= UNMAPPED_THRESHOLD):
        if (read2_idx <= read1_idx):
            return "B" # Read2 before Read1
        if (is_read1_inv or is_read2_inv):
            return "I" # Inversion
        if (read2_idx - read1_idx < len(read1) + normal_space):
            return "S" # Short
        if (read2_idx - read1_idx > len(read1) + normal_space):
            return "L" # Long
        if (p1 >= MAPPED_THRESHOLD and p2 >= MAPPED_THRESHOLD):
            return "M" # Mapped
        if (p1 >= MAPPED_THRESHOLD and p2 >= UNMAPPED_THRESHOLD):
            return "R1"
        if (p1 >= MAPPED_THRESHOLD and p2 < UNMAPPED_THRESHOLD):
            return "R2"
        if (p1 >= UNMAPPED_THRESHOLD and p2 >= MAPPED_THRESHOLD):
            return "L1"
        if (p1 < UNMAPPED_THRESHOLD and p2 >= MAPPED_THRESHOLD):
            return "L2"
    return "U" # Unmapped

def visualize_read_mapping(read1, is_read1_inv, read1_idx, read1_score, read2, is_read2_inv, read2_idx, read2_score, type):
    if not is_read1_inv:
        print(' '*read1_idx + read1 + ' /R1 /T=' + type + ' /S=' + str(read1_score))
    else:
        print(' '*read1_idx + read1[::-1] + ' /IR1 /T=' + type + ' /S=' + str(read1_score))
    if not is_read2_inv:
        print(' '*read2_idx + read2 + ' /R2 /T=' + type + ' /S=' + str(read2_score))
    else:
        print(' '*read2_idx + read2[::-1] + ' /IR2 /T=' + type + ' /S=' + str(read2_score))

def get_reads_maping_data(reads, ref):
    data_list = [] # list of [ (read1,is_read1_inv,read1_idx,read1_score) , (read2,is_read2_inv,read2_idx,read2_score) ]
    space_list = [] # list of distance between read1 and read 2
    for line in reads:
        read1, read2 = line.split(',')

        # calculate (max_score, best_idx) for each read and read inverse
        read1_map = read_mapping(read1, ref)
        read1_inv_map = read_mapping(read1[::-1], ref)
        read2_map = read_mapping(read2, ref)
        read2_inv_map = read_mapping(read2[::-1], ref)

        # set data is_read_inv, read_idx, read_score by comparing score between inverse and not inverse
        is_read1_inv = True if (read1_inv_map[0] > read1_map[0]) else False
        is_read2_inv = True if (read2_inv_map[0] > read2_map[0]) else False
        read1_idx = read1_inv_map[1] if (read1_inv_map[0] > read1_map[0]) else read1_map[1]
        read2_idx = read2_inv_map[1] if (read2_inv_map[0] > read2_map[0]) else read2_map[1]
        read1_score = read1_inv_map[0] if (read1_inv_map[0] > read1_map[0]) else read1_map[0]
        read2_score = read2_inv_map[0] if (read2_inv_map[0] > read2_map[0]) else read2_map[0]

        # calculate distance (space) between read1 and read 2 
        space = read2_idx - read1_idx - len(read1)
        space_list.append(space)
        data_list.append([ (read1,is_read1_inv,read1_idx,read1_score) , (read2,is_read2_inv,read2_idx,read2_score) ])
    return data_list, max(set(space_list), key=space_list.count) #normal distance = the most frequent number

def get_type_count(data_list, normal_space, ref):
    # find and count type from every reads
    type_count = {"B":0,"I":0,"S":0,"L":0,"M":0,"R1":0,"R2":0,"L1":0,"L2":0,"U":0}
    breakpoint = {"R":[], "L":[]}

    for (data_read1, data_read2) in data_list:
        read1, is_read1_inv, read1_idx, read1_score = data_read1[0], data_read1[1], data_read1[2], data_read1[3]
        read2, is_read2_inv, read2_idx, read2_score = data_read2[0], data_read2[1], data_read2[2], data_read2[3]
        type = get_mapping_type(read1, read1_idx, is_read1_inv, read2, read2_idx, is_read2_inv, normal_space, ref)
        type_count[type] += 1

        if (type == "R1"):
            breakpoint["R"].append(read2_idx + get_breakpoint_index(read2, ref[read2_idx:read2_idx+len(read2)], True))
        elif (type == "L1"):
            breakpoint["L"].append(read1_idx + get_breakpoint_index(read1, ref[read1_idx:read1_idx+len(read1)], False))

        if (DEBUG_MODE):
            visualize_read_mapping(read1, is_read1_inv, read1_idx, read1_score, read2, is_read2_inv, read2_idx, read2_score, type)
    if (DEBUG_MODE): 
        print(type_count)
        print(breakpoint)
    return (type_count, breakpoint)

def get_SV(type_count, breakpoint, ref):
    # find SV from type_count and breakpoint
    if (len(breakpoint["R"]) == len(set(breakpoint["R"]))): # Is not dupe
        if (len(breakpoint["R"]) == 0):
            breakpoint_R = len(ref)
        else:
            breakpoint_R = sorted(breakpoint["R"])[(len(breakpoint["R"])-1)//2] # medium
    else:
        breakpoint_R = max(set(breakpoint["R"]), key=breakpoint["R"].count, default=len(ref)) # mode
    if (len(breakpoint["L"]) == len(set(breakpoint["L"]))): # Is not dupe
        if (len(breakpoint["L"]) == 0):
            breakpoint_L = len(ref)
        else:
            breakpoint_L = sorted(breakpoint["L"])[(len(breakpoint["L"])-1)//2] # medium
    else:
        breakpoint_L = max(set(breakpoint["L"]), key=breakpoint["L"].count, default=len(ref)) #mode
    sum_SLBI = type_count["S"]+type_count["L"]+type_count["B"]+type_count["I"]

    if (DEBUG_MODE):
        print("breakpoint R, L, sum_SLBI =", breakpoint_R, breakpoint_L, sum_SLBI)
    
    if (len(breakpoint["R"]) < len(breakpoint["L"])*0.1 or len(breakpoint["R"])*0.1 > len(breakpoint["L"])):
        if (len(breakpoint["R"]) < len(breakpoint["L"])*0.1):
            return "Chromosomal translocation from index " + str(breakpoint_L)
        else:
            return "Chromosomal translocation from index " + str(breakpoint_R)

    if (type_count["L"] > sum_SLBI*0.55):
        return "Deletion from index " + str(breakpoint_R) + " to " + str(breakpoint_L)
    if (type_count["I"] > sum_SLBI*0.4):
        return "Inversion from index " + str(breakpoint_R) + " to " + str(breakpoint_L)
    if (type_count["B"] > sum_SLBI*0.55):
        return "Tandem duplication from index " + str(breakpoint_L) + " to " + str(breakpoint_R)

    if (type_count["S"] > sum_SLBI*0.55):
        return "Insertion (length < insert size) between index " + str(breakpoint_L) + " and " + str(breakpoint_R)
    else:
        return "Insertion (length >= insert size) between index " + str(breakpoint_L) + " and " + str(breakpoint_R)


data_list, normal_space = get_reads_maping_data(reads, ref)
type_count, breakpoint = get_type_count(data_list, normal_space, ref)
print(get_SV(type_count, breakpoint, ref))