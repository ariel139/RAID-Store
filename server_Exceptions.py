class SizeToLow(Exception):
    pass

class GeneralError(Exception):
    pass

# DataBase Errors

class UserDoesNotExsit(Exception):
    pass

class UserAlreadyExsit(Exception):
    pass

class UnknownError(Exception):
    pass

class InValidMessageFormat(Exception):
    pass

class NoNodescurrentluConnected(Exception):
    pass

class FileToLargeForPC(Exception):
    pass
class SumOfDrivesIncompitable(Exception):
    pass # describes a case when the sum of sizes of the drives is larger then the space granted by the user at start
class DeviceAlreadyExsits(Exception):
    pass