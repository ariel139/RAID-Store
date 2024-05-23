from datetime import datetime
from enum import Enum
from pathlib import Path
from os import mkdir
LOGS_FOLDER = Path('.') / 'logs'

def _create_log_folder():
    LOGS_FOLDER.mkdir(exist_ok=True)

class LOGS(Enum):
    INFO = 1
    WARNING=2
    DEBUG=3
    ERROR=4
def get_log_file_path():
    _create_log_folder()
    now = datetime.now()
    log_file_name = now.strftime("%Y-%m-%d")
    return log_file_name+'.log'

def get_current_time_string():
    return datetime.now().strftime("%Y-%m-%d-%H:%M:%S")

def create_log(log_type:LOGS, info:str,file_name:str=get_log_file_path() ):
    with open(LOGS_FOLDER/file_name,'a') as file:
        file.write(f"---{log_type.name}---{get_current_time_string()}---{info}\n\n")
        
if __name__ == "__main__":
    create_log(LOGS.ERROR,'hlle')
