"""
This class provides a wrapper for creating and managing Windows semaphores.

Attributes:
    None

Methods:
    __init__: Initializes the Semaphore object.
    open_semaphore: Opens an existing semaphore.
    acquire: Acquires the semaphore.
    release: Releases the semaphore.
    delete: Closes the semaphore handle.
    __delattr__: Deletes the semaphore.

"""

import win32event
from win32security import PyCredHandleType
from win32api import CloseHandle


class Semaphore:
    def __init__(self, semaphore_name: str, initial_value: int=1, maximum_value: int=1, semaphore_attributes=None):
        """
        Initializes the Semaphore object.

        Args:
            semaphore_name (str): The name of the semaphore.
            initial_value (int): The initial value of the semaphore.
            maximum_value (int): The maximum value of the semaphore.
            semaphore_attributes: Additional security attributes for the semaphore.
        """
        try:
            self.semaphore_handle = self.open_semaphore(semaphore_name)
        except Exception:
            if semaphore_attributes is not None:
                if not isinstance(semaphore_attributes, PyCredHandleType):
                    raise Exception('Unsupported type of security attributes')
            self.semaphore_handle = win32event.CreateSemaphore(semaphore_attributes, initial_value, maximum_value, semaphore_name)

    def open_semaphore(cls, semaphore_name: str, desired_access=win32event.EVENT_ALL_ACCESS, inherit_flag=True):
        """
        Opens an existing semaphore.

        Args:
            semaphore_name (str): The name of the semaphore.
            desired_access: Desired access rights for the semaphore.
            inherit_flag: Flag indicating whether the handle can be inherited.

        Returns:
            PyHANDLE: The handle to the semaphore.
        """
        return win32event.OpenSemaphore(desired_access, inherit_flag, semaphore_name)

    def acquire(self, maximum_waiting=win32event.INFINITE):
        """
        Acquires the semaphore.

        Args:
            maximum_waiting: Maximum time to wait for the semaphore.

        Raises:
            Exception: If there is an error acquiring the semaphore.
        """
        response = win32event.WaitForSingleObject(self.semaphore_handle, maximum_waiting)
        if response != win32event.WAIT_OBJECT_0:
            raise Exception(f'Error in semaphore acquiring: {response}')

    def release(self, semaphore_handle=None, release_amount=1):
        """
        Releases the semaphore.

        Args:
            semaphore_handle: The handle to the semaphore.
            release_amount (int): The number of semaphore releases.

        Raises:
            Exception: If there is an error releasing the semaphore.
        """
        if semaphore_handle is None:
            semaphore_handle = self.semaphore_handle
        else:
            if type(semaphore_handle) != int:
                raise Exception('The semaphore handle type is not correct')
        if release_amount != 1:
            print('WARNING: a none 1 release amount can cause problems')

        win32event.ReleaseSemaphore(semaphore_handle, release_amount)
        
    def delete(self):
        """
        Closes the semaphore handle.
        """
        CloseHandle(self.semaphore_handle)
    
    def __delattr__(self):
        """
        Deletes the semaphore.
        """
        self.delete()
