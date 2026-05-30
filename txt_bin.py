import struct

with open('задание1/random_numbers.txt', 'r') as f:
    numbers = [int(line.strip()) for line in f]

with open('задание1/random_numbers.bin', 'wb') as f:
    for num in numbers:
        f.write(struct.pack('q', num))