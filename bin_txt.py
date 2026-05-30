import struct

INT_SIZE = 8 

with open('задание1/random_numbers_sorted.bin', 'rb') as f:
    data = f.read()
    count = len(data) // INT_SIZE
    numbers = struct.unpack(f'{count}q',data)
with open('задание1/random_numbers_sorted.txt', 'w') as f:
    for num in numbers:
        f.write(f'{num}\n')