# edit file path
REF = 'ref.txt'
READ = 'read.txt'
DEBUG_MODE = False #True/False

with open(REF) as f:
    ref = f.read().splitlines()[0]
with open(READ) as f:
    reads = f.read().splitlines()

def get_score(read, ref_part):
    score = 0
    for i in range(len(ref_part)):
        if read[i] == ref_part[i]:
            score += 1
    return score

def read_mapping(read, ref):
    max_score, best_idx = (-1, -1)
    for i in range(len(ref) - len(read) + 1):
        score = get_score(read, ref[i:i+len(read)])
        if score > max_score:
            max_score = score
            best_idx = i
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
    normal length space between read1 and read2 = ---
    short length space between read1 and read2 = -
    long length space between read1 and read2 = ------
    any length space between read1 and read2 = -?-
    mapped = <    ]
    soft-clipped = <  ##]
    unmapped = <####]
    any = <  ? ]

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
    mapped_threshold = 0.85
    unmapped_threshold = 0.6

    if (p1 >= unmapped_threshold or p2 >= unmapped_threshold):
        if (read2_idx <= read1_idx):
            return "B"
        if (is_read1_inv or is_read2_inv):
            return "I"
        if (read2_idx - read1_idx < len(read1) + normal_space):
            return "S"
        if (read2_idx - read1_idx > len(read1) + normal_space):
            return "L"
        if (p1 >= mapped_threshold and p2 >= mapped_threshold):
            return "M"
        if (p1 >= mapped_threshold and p2 >= unmapped_threshold):
            return "R1"
        if (p1 >= mapped_threshold and p2 < unmapped_threshold):
            return "R2"
        if (p1 >= unmapped_threshold and p2 >= mapped_threshold):
            return "L1"
        if (p1 < unmapped_threshold and p2 >= mapped_threshold):
            return "L2"
    return "U"

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
    data_list = [] 
    space_list = []
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

        space = read2_idx - read1_idx - len(read1)
        space_list.append(space)
        data_list.append([ (read1,is_read1_inv,read1_idx,read1_score) , (read2,is_read2_inv,read2_idx,read2_score) ])
    return data_list, max(set(space_list), key=space_list.count) #normal length space

def get_type_count(data_list, normal_space, ref):
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
    breakpoint_R = max(set(breakpoint["R"]), key=breakpoint["R"].count, default=len(ref))
    breakpoint_L = max(set(breakpoint["L"]), key=breakpoint["L"].count, default=len(ref))

    sum_SLBI = type_count["S"]+type_count["L"]+type_count["B"]+type_count["I"]
    
    if (type_count["L"] > sum_SLBI*0.8 and breakpoint_L > breakpoint_R):
        return "Deletion from index " + str(breakpoint_R) + " to " + str(breakpoint_L)
    elif (type_count["I"] > sum_SLBI*0.8 and breakpoint_L > breakpoint_R):
        return "Inversion from index " + str(breakpoint_R) + " to " + str(breakpoint_L)
    elif (type_count["B"] > sum_SLBI*0.8 and breakpoint_R > breakpoint_L):
        return "Tandem duplication from index " + str(breakpoint_L) + " to " + str(breakpoint_R)

    if (len(breakpoint["R"]) == 0 or len(breakpoint["L"]) == 0):
        if (len(breakpoint["R"]) == 0):
            return "Chromosomal translocation from index " + str(breakpoint_L)
        else:
            return "Chromosomal translocation from index " + str(breakpoint_R)

    if (abs(breakpoint_R-breakpoint_L) <= 2):
        if (type_count["S"] > sum_SLBI*0.8):
            return "Insertion (length < insert size) between index " + str(breakpoint_L) + " and " + str(breakpoint_R)
        else:
            return "Insertion (length >= insert size) between index " + str(breakpoint_L) + " and " + str(breakpoint_R)

    return "Unknown SV"

if (DEBUG_MODE):
    print(ref)
data_list, normal_space = get_reads_maping_data(reads, ref)
type_count, breakpoint = get_type_count(data_list, normal_space, ref)
print(get_SV(type_count, breakpoint, ref))