import mmap
from os.path import exists
from server_Exceptions import FileToLargeForPC
ALL_ACCESS = mmap.ACCESS_COPY |mmap.ACCESS_READ | mmap.ACCESS_WRITE
class SharedMemory:
    def __init__(self, name:str, size=0,file: bool = False) -> None:
        try:
            self.size = 0 if size==0 else size
            if file:
                if not exists(name):
                    raise ValueError('file does not exsit:cannot mmap an empty file')
                with open(name,'r+b') as file:
                    self.handle = mmap.mmap(file.fileno(),self.size)
            else: 
                self.handle = mmap.mmap(-1,self.size, tagname=name, access= mmap.ACCESS_WRITE)
            self.name = name
            self.read_cursor = 0
            self.write_cursor = 0
        except OSError as err:
            if '1450' in err:
                raise FileToLargeForPC()

        
    def read(self,size:int):
        if size == 0:
            raise ValueError('Must have a greater then 0 size')
        end_index = self.read_cursor+size
        data = self.handle[self.read_cursor:min(self.size,end_index)]
        self._zero_memory_buffer(min(self.size,end_index))
        if end_index >= self.size:
            self.read_cursor = end_index % self.size
            data+= self.handle[:self.read_cursor]
            self._zero_memory_buffer(self.read_cursor,start=0)
        else:
            self.read_cursor +=size
        return data

    def _zero_memory_buffer(self,end:int,start:int =-1):
        if start == -1:
            start = self.read_cursor
        length = end-start
        self.handle[start:end] = bytes(length)

    def write(self, buffer: bytes):
        try:
            length = len(buffer)
            if length+self.write_cursor >= self.size:
                self.handle[self.write_cursor:] = buffer[:self.size-self.write_cursor]
                self.write_cursor =length%self.size
            else:
                self.handle[self.write_cursor:self.write_cursor+length] = buffer[:length]
                self.write_cursor += length
        except ValueError as err:
            print('Unable to write to memory error: ',err)
        except TypeError as err:
            print('Unable to read, the object is read only')
    
    def close(self):
        if self.handle:
            self.handle.close()
    
    def __del__(self,):
        self.close()
    def __len__(self):
        return self.size

    def __getitem__(self, key):
        if isinstance(key, slice):
            start, stop, step = key.start, key.stop, key.step
            # Perform custom slicing logic
            sliced_data = self.handle[start:stop:step]
            return sliced_data
        else:
            # Handle single index
            return self.data[key]

