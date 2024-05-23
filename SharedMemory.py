"""
This class provides a wrapper for creating and managing shared memory using mmap in Python.

Attributes:
    None

Methods:
    __init__: Initializes the SharedMemory object.
    read: Reads data from the shared memory.
    write: Writes data to the shared memory.
    close: Closes the shared memory handle.
    __del__: Deletes the shared memory.
    __len__: Returns the size of the shared memory.
    __getitem__: Gets an item from the shared memory.
"""

import mmap
from os.path import exists
from server_Exceptions import FileToLargeForPC

ALL_ACCESS = mmap.ACCESS_COPY | mmap.ACCESS_READ | mmap.ACCESS_WRITE

class SharedMemory:
    def __init__(self, name: str, size=0, file: bool = False) -> None:
        """
        Initializes the SharedMemory object.

        Args:
            name (str): The name of the shared memory.
            size (int): The size of the shared memory.
            file (bool): Indicates whether to use a file for shared memory.
        """
        try:
            self.size = 0 if size == 0 else size
            if file:
                if not exists(name):
                    raise ValueError('file does not exist: cannot mmap an empty file')
                with open(name, 'r+b') as file:
                    self.handle = mmap.mmap(file.fileno(), self.size)
            else: 
                self.handle = mmap.mmap(-1, self.size, tagname=name, access=mmap.ACCESS_WRITE)
            self.name = name
            self.read_cursor = 0
            self.write_cursor = 0
        except OSError as err:
            if '1450' in str(err):
                raise FileToLargeForPC()

    def read(self, size: int):
        """
        Reads data from the shared memory.

        Args:
            size (int): The size of the data to read.

        Returns:
            bytes: The data read from the shared memory.
        """
        if size == 0:
            raise ValueError('Must have a greater than 0 size')
        end_index = self.read_cursor + size
        data = self.handle[self.read_cursor:min(self.size, end_index)]
        self._zero_memory_buffer(min(self.size, end_index))
        if end_index >= self.size:
            self.read_cursor = end_index % self.size
            data += self.handle[:self.read_cursor]
            self._zero_memory_buffer(self.read_cursor, start=0)
        else:
            self.read_cursor += size
        return data

    def _zero_memory_buffer(self, end: int, start: int = -1):
        """
        Zeroes out memory buffer.

        Args:
            end (int): The end index.
            start (int): The start index.

        """
        if start == -1:
            start = self.read_cursor
        length = end - start
        self.handle[start:end] = bytes(length)

    def write(self, buffer: bytes):
        """
        Writes data to the shared memory.

        Args:
            buffer (bytes): The data to write to the shared memory.
        """
        try:
            length = len(buffer)
            if length + self.write_cursor >= self.size:
                self.handle[self.write_cursor:] = buffer[:self.size - self.write_cursor]
                self.write_cursor = length % self.size
            else:
                self.handle[self.write_cursor:self.write_cursor + length] = buffer[:length]
                self.write_cursor += length
        except ValueError as err:
            print('Unable to write to memory error: ', err)
        except TypeError as err:
            print('Unable to read, the object is read only')

    def close(self):
        """
        Closes the shared memory handle.
        """
        if self.handle:
            self.handle.close()

    def __del__(self):
        """
        Deletes the shared memory.
        """
        self.close()

    def __len__(self):
        """
        Returns the size of the shared memory.
        """
        return self.size

    def __getitem__(self, key):
        """
        Gets an item from the shared memory.

        Args:
            key: The key to access the item.

        Returns:
            bytes: The item from the shared memory.
        """
        if isinstance(key, slice):
            start, stop, step = key.start, key.stop, key.step
            # Perform custom slicing logic
            sliced_data = self.handle[start:stop:step]
            return sliced_data
        else:
            # Handle single index
            return self.data[key]

if __name__ == "__main__":
    print(SharedMemory.__doc__)