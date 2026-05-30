import os
import struct
import heapq
import tempfile
from multiprocessing import Process
from multiprocessing.managers import BaseManager, NamespaceProxy

INT_SIZE = 8

class SharedChunk:

    def __init__(self, data, index):
        self.data = data
        self.index = index
        self.temp_file = None

class ChunkProxy(NamespaceProxy):

    _exposed_ = (
        '__getattribute__',
        '__setattr__',
        '__delattr__'
    )

class MyManager(BaseManager):
    pass

MyManager.register(
    'SharedChunk',
    SharedChunk,
    ChunkProxy
)

def worker(chunk, temp_dir):

    if len(chunk.data) % INT_SIZE != 0:
        print("Wrong data size")
        return
    
    numbers = list(
        struct.unpack(f'{len(chunk.data)//INT_SIZE}q', chunk.data))

    numbers.sort()

    temp_file = os.path.join(temp_dir, f'chunk_{chunk.index}.bin')

    with open(temp_file, 'wb') as f:
        packed_data = struct.pack(f'{len(numbers)}q', *numbers)
        f.write(packed_data)

    chunk.temp_file = temp_file

    print(f'Chunk {chunk.index} sorted')

def merge_files(temp_files, output_file):

    files = []
    for f in temp_files:
        files.append(open(f, 'rb'))

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
                heapq.heappush(heap, (next_num, file_index))

    for f in files:
        f.close()

def external_sort(input_file, chunk_size):

    manager = MyManager()
    manager.start()

    temp_dir = tempfile.mkdtemp()
    chunk_bytes = chunk_size * INT_SIZE

    chunks = []

    with open(input_file, 'rb') as f:
        index = 0
        while True:
            data = f.read(chunk_bytes)
            if not data:
                break

            chunk = manager.SharedChunk(data, index)
            chunks.append(chunk)
            index += 1

    processes = []
    for chunk in chunks:
        p = Process(target=worker, args=(chunk, temp_dir))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    temp_files = []
    for chunk in chunks:
        temp_files.append(chunk.temp_file)

    output_file = 'задание1/random_numbers_sorted.bin'
    merge_files(temp_files, output_file)

    print('DONE')

if __name__ == '__main__':

    input_file = 'задание1/random_numbers.bin' 
    chunk_size = 10000
    external_sort(input_file, chunk_size)