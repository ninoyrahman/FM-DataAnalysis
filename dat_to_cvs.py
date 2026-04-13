import numpy as np
import scipy as sp
import pandas as pd

# read file names for concat
filename_1 = input('first file name: ')
filename_2 = input('second file name: ')
filename_3 = input('third file name: ')

# print file names
print('file names:')
print(filename_1)
print(filename_2)
print(filename_3)

# filename_1 = "raw_data/FM2025_0448_PP_(La0.9Ce0.1)1.06Fe12B6_M-T(0.02,1,2,5,10T)_2.878mg.dat"
# filename_2 = "raw_data/FM2025_0448_PP_(La0.9Ce0.1)1.06Fe12B6_M-T(0.25-6T)_2.859mg.dat"
# filename_3 = "raw_data/FM2025_0448_PP_(La0.9Ce0.1)1.06Fe12B6_M-T(6.25-9.75T)_2.859mg.dat"

# read input files
f1 = open(filename_1, 'r')
f2 = open(filename_2, 'r')
f3 = open(filename_3, 'r')

# create output file
f4 = open('raw_data/combined_raw_data.cvs', 'w')

# find header for first file
for _ in range(40):
    line = f1.readline()

    if line.rstrip() == "[Data]":
        break

# write first file
for line in f1:
    f4.write(line)

# find header for second file
for _ in range(40):
    line = f2.readline()

    if line.rstrip() == "[Data]":
        break

# write second file
line = f2.readline()
for line in f2:
    f4.write(line)

# find header for third file
for _ in range(40):
    line = f3.readline()

    if line.rstrip() == "[Data]":
        break

# write third file
line = f3.readline()
for line in f3:
    f4.write(line)

f1.close()
f2.close()
f3.close()
f4.close()