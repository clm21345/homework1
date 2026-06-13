import os
import struct
import heapq
import tempfile
from multiprocessing import Process

INT_SIZE = 8


def worker(data, index, temp_dir):

    if len(data) % INT_SIZE != 0:
        print("Wrong data size")
        return

    numbers = list(
        struct.unpack(f'{len(data)//INT_SIZE}q', data)
    )

    numbers.sort()

    temp_file = os.path.join(
        temp_dir,
        f'chunk_{index}.bin'
    )

    with open(temp_file, 'wb') as f:
        packed_data = struct.pack(f'{len(numbers)}q', *numbers)
        f.write(packed_data)

    print(f'Chunk {index} sorted')


def merge_files(temp_files, output_file):

    files = []

    for file_name in temp_files:
        files.append(open(file_name, 'rb'))

    heap = []

    for i, f in enumerate(files):
        data = f.read(INT_SIZE)

        if data:
            num = struct.unpack('q', data)[0]
            heapq.heappush(heap, (num, i))

    with open(output_file, 'wb') as out:

        while heap:

            num, file_index = heapq.heappop(heap)

            out.write(struct.pack('q', num))

            data = files[file_index].read(INT_SIZE)

            if data:
                next_num = struct.unpack('q', data)[0]
                heapq.heappush(
                    heap,
                    (next_num, file_index)
                )

    for f in files:
        f.close()


def external_sort(input_file, chunk_size):

    temp_dir = tempfile.mkdtemp()

    chunk_bytes = chunk_size * INT_SIZE

    chunks = []

    with open(input_file, 'rb') as f:

        index = 0

        while True:

            data = f.read(chunk_bytes)

            if not data:
                break

            chunks.append((data, index))
            index += 1

    processes = []

    for data, index in chunks:

        p = Process(
            target=worker,
            args=(data, index, temp_dir)
        )

        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    temp_files = []

    for data, index in chunks:
        temp_files.append(os.path.join(temp_dir, f'chunk_{index}.bin'))

    output_file = 'задание1/random_numbers_sorted.bin'

    merge_files(
        temp_files,
        output_file
    )

    print('DONE')


if __name__ == '__main__':

    input_file = 'задание1/random_numbers.bin'

    chunk_size = 10000

    external_sort(input_file, chunk_size)