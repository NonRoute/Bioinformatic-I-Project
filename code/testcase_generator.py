import random
from variance_type import VarianceType

# edit settings


MODE = 0


# Generate reference & variance
def generateReference(length):
    BASES = ["A", "C", "G", "T"]
    output = ""
    for i in range(length):
        output += random.choice(BASES)
    return output


def generateRead(index, physical, reads, anwserSplit, READ_LENGTH, READ_DISTANCE, ERROR_RATE):
    NEG_BASES = {"A": ["C", "G", "T"], "C": ["A", "G", "T"], "G": ["A", "C", "T"], "T": ["A", "C", "G"]}

    read1 = ""
    for i in range(index, index + READ_LENGTH):
        if random.random() < ERROR_RATE:
            read1 += random.choice(NEG_BASES[physical[i]])
        else:
            read1 += physical[i]

    read2 = ""
    for i in range(index + READ_LENGTH + READ_DISTANCE, index + READ_LENGTH * 2 + READ_DISTANCE):
        if random.random() < ERROR_RATE:
            read2 += random.choice(NEG_BASES[physical[i]])
        else:
            read2 += physical[i]

    reads.append([read1, read2])
    line = " " * index + read1 + " " * READ_DISTANCE + read2
    anwserSplit.append(line)


def generate_testcase(
    file_path: str,
    file_suffix: str,
    MODE: int,
    READ_LENGTH: int,
    READ_DISTANCE: int,
    REF_LENGTH: int,
    VARIANT_SIZE: int,
    VARIANT_PADDING: int,
    SHIFT_MIN: int,
    SHIFT_MAX: int,
    SHUFFLE_READS=True,
    ERROR_RATE=0.01,
) -> tuple[VarianceType, int, int, int]:
    readsPath = "read"
    anwserPath = "anwser"
    refPath = "ref"
    readsPath += "_" + file_suffix
    anwserPath += "_" + file_suffix
    refPath += "_" + file_suffix

    ref = generateReference(REF_LENGTH)

    anwser = ""
    output = []

    if MODE == 0:
        index = random.randint(VARIANT_PADDING, len(ref) - VARIANT_PADDING - 1 - VARIANT_SIZE)
        anwser += "Deletion at index " + str(index) + "\n"
        anwser += "With size " + str(VARIANT_SIZE) + "\n"
        anwser += ref[0:index] + ref[index + VARIANT_SIZE :]
        output = [VarianceType.DELETION, index, index + VARIANT_SIZE]
    elif MODE == 1:
        index = random.randint(VARIANT_PADDING, len(ref) - VARIANT_PADDING - 1)
        anwser += "Insertion at index " + str(index) + "\n"
        anwser += "With size " + str(VARIANT_SIZE) + "\n"
        anwser += ref[0:index] + generateReference(VARIANT_SIZE) + ref[index:]
        output = [VarianceType.INSERTION_BIGGER, index, index + 1]
    elif MODE == 2:
        index = random.randint(VARIANT_PADDING, len(ref) - VARIANT_PADDING - 1)
        anwser += "Insertion at index " + str(index) + "\n"
        anwser += "With size " + str(VARIANT_SIZE) + "\n"
        anwser += ref[0:index] + generateReference(VARIANT_SIZE) + ref[index:]
        output = [VarianceType.INSERTION_SMALLER, index, index + 1]
    elif MODE == 3:
        index = random.randint(VARIANT_PADDING, len(ref) - VARIANT_PADDING - 1 - VARIANT_SIZE)
        anwser += "Tandem Duplication at index " + str(index) + "\n"
        anwser += "With size " + str(VARIANT_SIZE) + "\n"
        anwser += ref[0:index] + ref[index : index + VARIANT_SIZE] + ref[index:]
        output = [VarianceType.TANDEM, index, index + VARIANT_SIZE]
    elif MODE == 4:
        index = random.randint(VARIANT_PADDING, len(ref) - VARIANT_PADDING - 1)
        anwser += "Inversion at index " + str(index) + "\n"
        anwser += "With size " + str(VARIANT_SIZE) + "\n"
        anwser += ref[0:index] + ref[index : index + VARIANT_SIZE][::-1] + ref[index + VARIANT_SIZE :]
        output = [VarianceType.INVERSION, index, index + VARIANT_SIZE]
    else:
        index = len(ref) - VARIANT_SIZE
        anwser += "Translocation at index " + str(index) + "\n"
        anwser += "With size " + str(VARIANT_SIZE) + "\n"
        anwser += ref[0:index] + generateReference(VARIANT_SIZE)
        output = [VarianceType.TRANSLOCATION, index, 0]

    anwser += "\n" + ref + "\n"
    count = 1
    for i in range(max(len(anwser.split("\n")[2]), len(anwser.split("\n")[3]))):
        if i % 5 == 4:
            anwser += str(count)
            count += 1
            count %= 10
        else:
            anwser += " "
    anwser += "\n" + " " * index + "^"
    anwserSplit = anwser.split("\n")
    anwserSplit = [anwserSplit[0], anwserSplit[1], anwserSplit[4], anwserSplit[3], anwserSplit[2], anwserSplit[5]]

    # Generate reads
    reads = []
    physical = anwserSplit[4]

    index = 0
    while index < len(physical) - 2 * READ_LENGTH - READ_DISTANCE - 1:
        generateRead(index, physical, reads, anwserSplit, READ_LENGTH, READ_DISTANCE, ERROR_RATE)
        index += random.randint(SHIFT_MIN, SHIFT_MAX)

    index = len(physical) - 2 * READ_LENGTH - READ_DISTANCE
    generateRead(index, physical, reads, anwserSplit, READ_LENGTH, READ_DISTANCE, ERROR_RATE)

    if SHUFFLE_READS:
        random.shuffle(reads)

    readsText = "\n".join(",".join(row) for row in reads)
    anwser = '\n'.join(anwserSplit)

    # print("-----------{} reads-----------".format(len(reads)))
    # print(readsText)
    # print("\n-----------Anwser-----------")
    # print(anwser)
    # print("\n".join(anwser.split("\n")[:6]))

    # Save files
    if readsPath:
        with open(file_path + readsPath + ".txt", "w") as f:
            f.write(readsText)
    if anwserPath:
        with open(file_path + anwserPath + ".txt", "w") as f:
            f.write(anwser)
    if refPath:
        with open(file_path + refPath + ".txt", "w") as f:
            f.write(ref)
    
    output.append(len(reads))

    return tuple(output)
