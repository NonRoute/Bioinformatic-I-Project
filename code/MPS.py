with open('ref.txt') as f:
    ref = f.read().splitlines()[0]
with open('deletion_1_read.txt') as f:
    reads = f.read().splitlines()
print(ref)

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

def get_percent_match(read, ref_part):
    percent = 0
    for i in range(len(read)):
        if read[i] == ref_part[i]:
            percent += 1
    return percent/len(read)

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
    if (read2_idx < read1_idx):
        return "B"
    if (is_read1_inv or is_read2_inv):
        return "I"
    if (read2_idx - read1_idx < len(read1) + normal_space):
        return "S"
    if (read2_idx - read1_idx > len(read1) + normal_space):
        return "L"
    p1 = get_percent_match(read1,ref[read1_idx:read1_idx+len(read1)])
    p2 = get_percent_match(read2,ref[read2_idx:read2_idx+len(read2)])
    mapped_threshold = 0.8
    unmapped_threshold = 0.3
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

def visualize_read_mapping(read1, read1_idx, is_read1_inv, read2, read2_idx, is_read2_inv, type):
    if not is_read1_inv:
        print(' '*read1_idx + read1 + '/1=' + type)
    else:
        print(' '*read1_idx + read1[::-1] + '/r1=' + type)
    if not is_read2_inv:
        print(' '*read2_idx + read2 + '/2=' + type)
    else:
        print(' '*read2_idx + read2[::-1] + '/r2=' + type)

def get_reads_maping_idx(reads):
    data_list = [] 
    space_list = []
    for line in reads:
        read1, read2 = line.split(',')

        #calculate max_score, best_idx for each read and read inverse
        read1_map = read_mapping(read1, ref)
        read1_inv_map = read_mapping(read1[::-1], ref)
        read2_map = read_mapping(read2, ref)
        read2_inv_map = read_mapping(read2[::-1], ref)

        is_read1_inv = True if (read1_inv_map[0] > read1_map[0]) else False
        is_read2_inv = True if (read2_inv_map[0] > read2_map[0]) else False
        read1_idx = read1_inv_map[1] if (read1_inv_map[0] > read1_map[0]) else read1_map[1]
        read2_idx = read2_inv_map[1] if (read2_inv_map[0] > read2_map[0]) else read2_map[1]

        space = read2_idx - read1_idx - len(read1)
        space_list.append(space)
        data_list.append([ (read1,is_read1_inv,read1_idx) , (read2,is_read2_inv,read2_idx) ])
    return data_list, max(set(space_list), key=space_list.count) #normal length space

def get_type_count(data_list, normal_space):
    type_count = {"B":0,"I":0,"S":0,"L":0,"M":0,"R1":0,"R2":0,"L1":0,"L2":0,"U":0}
    for (data_read1, data_read2) in data_list:
        read1, is_read1_inv, read1_idx = data_read1[0], data_read1[1], data_read1[2]
        read2, is_read2_inv, read2_idx = data_read2[0], data_read2[1], data_read2[2]
        type = get_mapping_type(read1, read1_idx, is_read1_inv, read2, read2_idx, is_read2_inv, normal_space, ref)
        type_count[type] += 1
        # visualize_read_mapping(read1, read1_idx, is_read1_inv, read2, read2_idx, is_read2_inv,type)
    print(type_count)
    '''
    Del = {'B': 0, 'I': 1, 'S': 0, 'L': 5, 'M': 6, 'R1': 1, 'R2': 0, 'L1': 2, 'L2': 0, 'U': 0}
    Del0 = {'B': 0, 'I': 0, 'S': 0, 'L': 4, 'M': 28, 'R1': 0, 'R2': 0, 'L1': 0, 'L2': 0, 'U': 0}
    InsG = {'B': 5, 'I': 4, 'S': 1, 'L': 2, 'M': 17, 'R1': 1, 'R2': 0, 'L1': 1, 'L2': 0, 'U': 0}
    InsL = {'B': 1, 'I': 0, 'S': 2, 'L': 4, 'M': 17, 'R1': 1, 'R2': 0, 'L1': 2, 'L2': 0, 'U': 0}
    Inv = {'B': 3, 'I': 9, 'S': 0, 'L': 1, 'M': 10, 'R1': 0, 'R2': 0, 'L1': 1, 'L2': 0, 'U': 0}
    Dup = {'B': 6, 'I': 0, 'S': 1, 'L': 1, 'M': 23, 'R1': 0, 'R2': 0, 'L1': 1, 'L2': 0, 'U': 0}
    Dup0 = {'B': 8, 'I': 1, 'S': 0, 'L': 0, 'M': 32, 'R1': 1, 'R2': 0, 'L1': 1, 'L2': 0, 'U': 0}
    Tra = {'B': 4, 'I': 9, 'S': 0, 'L': 0, 'M': 10, 'R1': 0, 'R2': 0, 'L1': 1, 'L2': 0, 'U': 0}
    '''
    return type_count

def get_SV(type_count):
    sum_SLBI = type_count["S"]+type_count["L"]+type_count["B"]+type_count["I"]
    sum_UR2L2 = type_count["U"]+type_count["R2"]+type_count["L2"]
    if (sum_UR2L2 < sum_SLBI):
        if (type_count["L"] > sum_SLBI*0.3):
            return "Deletion"
        elif (type_count["S"] > sum_SLBI*0.3):
            return "Insertion (length >= insert size)"
        elif (type_count["B"] > sum_SLBI*0.3):
            return "Tandem duplication" 
        elif (type_count["I"] > sum_SLBI*0.3):
            return "Inversion" 
    else:
        sum_R1R2 = type_count["R1"]+type_count["R2"]
        sum_L1L2 = type_count["L1"]+type_count["L2"]
        if (sum_R1R2 == 0 or sum_L1L2 == 0):
            return "Chromosomal translocation"
        else:
            return "Insertion (length < insert size)"

data_list, normal_space = get_reads_maping_idx(reads)
type_count = get_type_count(data_list, normal_space)
print(get_SV(type_count))
