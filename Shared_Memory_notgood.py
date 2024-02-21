import ctypes

# Constants
FILE_MAP_ALL_ACCESS = 0x000F0000
INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value
PAGE_READWRITE = 0x04

LPVOID = ctypes.c_void_p
SIZE_T = ctypes.c_size_t

# Load the kernel32.dll library
kernel32 = ctypes.WinDLL('kernel32.dll')

class Shared_Memory:
    # Function prototype
    CreateFileMapping = kernel32.CreateFileMappingW
    CreateFileMapping.argtypes = [
        ctypes.c_void_p,  # HANDLE hFile
        ctypes.c_void_p,  # LPSECURITY_ATTRIBUTES lpFileMappingAttributes
        ctypes.c_uint32,  # DWORD flProtect
        ctypes.c_uint32,  # DWORD dwMaximumSizeHigh
        ctypes.c_uint32,  # DWORD dwMaximumSizeLow
        LPVOID # LPCWSTR lpName
    ]
    CreateFileMapping.restype = ctypes.c_void_p  # HANDLE

    CloseHandle = kernel32.CloseHandle
    CloseHandle.argtypes = [ctypes.c_void_p]  # HANDLE
    CloseHandle.restype = ctypes.c_int  # BOOL

    # OpenFileMapping function prototype
    OpenFileMapping = kernel32.OpenFileMappingW
    OpenFileMapping.argtypes = [
        ctypes.c_uint32,  # DWORD dwDesiredAccess
        ctypes.c_int,     # BOOL bInheritHandle
        LPVOID # LPCWSTR lpName
    ]
    OpenFileMapping.restype = ctypes.c_void_p  # HANDLE
    
    # MapViewOfFile function prototype
    MapViewOfFile = kernel32.MapViewOfFile
    MapViewOfFile.argtypes = [
        ctypes.c_void_p,    # HANDLE hFileMappingObject
        ctypes.c_uint32,    # DWORD dwDesiredAccess
        ctypes.c_uint32,    # DWORD dwFileOffsetHigh
        ctypes.c_uint32,    # DWORD dwFileOffsetLow
        ctypes.c_uint32,    # SIZE_T dwNumberOfBytesToMap
    ]
    MapViewOfFile.restype = ctypes.c_void_p  # LPVOID

    # CopyMemory function prototype
    CopyMemory = ctypes.cdll.kernel32.RtlMoveMemory
    CopyMemory.argtypes = [
        LPVOID,  # Destination pointer
        LPVOID,  # Source pointer
        SIZE_T   # Number of bytes to copy
    ]
    CopyMemory.restype = None


    def __init__(self, name:str, size: int = 4096) -> None:
        # try:
        self.handle = Shared_Memory.OpenFileMapping(FILE_MAP_ALL_ACCESS,False,name.encode('utf-16-le'))
        if self.handle is None:
            try:
                self.handle = Shared_Memory.CreateFileMapping(INVALID_HANDLE_VALUE,None,PAGE_READWRITE,0,size,name.encode('utf-16-le'))
            except Exception:
                raise Exception("Failed to create file mapping object. Error code:", ctypes.GetLastError())
        # except Exception as err:
        #     raise Exception("Failed to open file mapping object. Error code:", ctypes.GetLastError())
        
        self.buf = Shared_Memory.MapViewOfFile(self.handle,FILE_MAP_ALL_ACCESS,0,0,4096)
        if self.buf is None:
            raise Exception("Failed to map thefile mapping object in the programms RAM. Error code:", ctypes.GetLastError())
        
        
    def read():
        pass

    def write(self,msg:str):
        if self.buf is not None:
            msg = msg.encode('utf-16-le')
            Shared_Memory.CopyMemory(msg,self.buf,len(msg))

shr = Shared_Memory('Ariel')
shr.write('Hello')
input()