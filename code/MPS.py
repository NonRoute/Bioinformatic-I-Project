with open('ref.txt') as f:
    ref = f.read().splitlines()[0]
with open('insertion_greater_1_read.txt') as f:
    read = f.read().splitlines()

def get_score(read, ref):
    score = 0
    for i in range(len(ref)):
        if read[i] == ref[i]:
            score += 1
    return score

def read_mapping(read, ref):
    max_score, best_position = (-1, -1)
    for i in range(len(ref) - len(read) + 1):
        score = get_score(read, ref[i:i+len(read)])
        if score > max_score:
            max_score = score
            best_position = i
    return (max_score, best_position)

def visualize_read_mapping(read, ref, index):
    out = ' '*len(ref)
    out = out[:index] + read + out[index + len(read) + 1:]
    print(out)

print(ref)
for line in read:
    read1, read2 = line.split(',')
    read1_rev, read2_rev = read1[::-1], read2[::-1]
    read1_map = read_mapping(read1, ref)
    read1_rev_map = read_mapping(read1_rev, ref)
    if (read1_map[0] > read1_rev_map[0]):
        visualize_read_mapping(read1+'/1='+str(read1_map[0]), ref, read1_map[1])
    else:
        visualize_read_mapping(read1+'/r1='+str(read1_rev_map[0]), ref, read1_map[1])

    read2_map = read_mapping(read2, ref)
    read2_rev_map = read_mapping(read2_rev, ref)
    if (read2_map[0] > read2_rev_map[0]):
        visualize_read_mapping(read2+'/2='+str(read2_map[0]), ref, read2_map[1])
    else:
        visualize_read_mapping(read2+'/r2='+str(read2_rev_map[0]), ref, read2_map[1])
