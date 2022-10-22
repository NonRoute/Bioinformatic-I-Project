ref = open("ref.txt", "r")
read1 = open("read1.txt", "r")
read2 = open("read2.txt", "r")
rread1 = read1[::-1]
rread2 = read2[::-1]
rlen = len(ref)
r1len = len(read1)
r2len = len(read2)
maxr1 = 0
maxr2 = 0
maxrr1 = 0
maxrr2 = 0
for i in range (0, rlen - r1len + 1):
    r1 = 0
    for j in range (0, r1len):
        while ref[i + j] == read1[j]:
            r1 += 1
    maxr1 = max(maxr1, r1)

for i in range (0, rlen - r2len + 1):
    r2 = 0
    for j in range (0, r2len):
        while ref[i + j] == read2[j]:
            r2 += 1
    maxr2 = max(maxr2, r2)

for i in range (0, rlen - r1len + 1):
    rr1 = 0
    for j in range (0, r1len):
        while ref[i + j] == rread1[j]:
            rr1 += 1
    maxrr1 = max(maxrr1, rr1)

for i in range (0, rlen - r2len + 1):
    rr2 = 0
    for j in range (0, rr2len):
        while ref[i + j] == rread2[j]:
            rr2 += 1
    maxrr2 = max(maxrr2, rr2)

maxr1 = max(maxr1, maxrr1)
maxr2 = max(maxr2, maxrr2)

print(maxr1)
print(maxr2)
