"""
This class represents data entities in the system.

Attributes:
    GET_FIELD_QUERY (str): SQL query template for retrieving a data field by ID.
    INSERT_FILED_NOT_PATH (str): SQL query template for inserting a data field without path information.
    INSERT_FILED (str): SQL query template for inserting a data field with path information.
    UPDATE_PATH_FILED (str): SQL query template for updating the path of a data field.
    GET_RECORDS (str): SQL query template for retrieving all data records.
    UPDATE_SIZE_BY_HASH_PATH_RELATION (str): SQL query template for updating the size of a data field based on hash, path, and relation.
    GET_DRIVE_USED_SIZE (str): SQL query template for retrieving the used size of a drive.

Methods:
    __init__: Constructor method to initialize a Data object.
    CreateField: Static method to create a data field with path information.
    CreateFieldNoPath: Static method to create a data field without path information.
    update_path_filed: Static method to update the path of a data field.
    get_data_records: Static method to retrieve all data records.
    _get_latest_record_id: Static method to retrieve the latest record ID.
    _get_file_data: Method to retrieve data from a file.
    update_size_by_hash_path_relation: Static method to update the size of a data field.
    get_drive_used_size: Static method to retrieve the used size of a drive.
"""

from DataBaseSession import DataBaseSession
from pathlib import Path
from uuid import getnode
from hashlib import sha256

MAC = hex(getnode()).encode()

class Data(DataBaseSession):
    GET_FIELD_QUERY = 'select * from data where id=%s;'
    INSERT_FILED_NOT_PATH = 'INSERT INTO data (hash, size, relation, location, parity) VALUES (%s, %s, %s, %s, %s);'
    INSERT_FILED = 'INSERT INTO Data (hash, size, relation, path, location, parity) VALUES (%s, %s, %s, %s, %s, %s);'
    UPDATE_PATH_FILED = "UPDATE data SET `path`=%s WHERE `id`=%s"
    GET_RECORDS = 'select id, path, size, relation from data;'
    UPDATE_SIZE_BY_HASH_PATH_RELATION = 'UPDATE data SET size = size + %s WHERE location = %s and path = %s and relation = %s'
    GET_DRIVE_USED_SIZE = 'SELECT SUM(size) FROM data WHERE location = %s'
    DRIVES_IDS = 'select location from data'
    DATA_CROSSING= """
                    select (
                    select mac from drives where drive_id=location
                    ) as 'mac', SUM(size)
                    from data
                    where relation=%s
                    GROUP BY location
                    """
    ACTUAL_DATA_SUM = 'SELECT SUM(size) from data where parity!=1'
    RECOVERD_DATA_COUNT = """SELECT SUM(size) from data where location IN (select real_drive_id from parties)"""
    CHECK_IF_DRIVE_USED_FOR_DATA= 'SELECT EXISTS( select * from data where location =%s and parity=0) '
    GET_FILE_RECORDS_FOR_DRIVE = 'SELECT * FROM raid.data where location=%s ORDER BY id;'
    def __init__(self, id_num: int):
        """
        Constructor method to initialize a Data object.

        Args:
            id_num (int): The ID of the data field.

        Attributes:
            hash_value (str): The hash value of the data.
            id_num (int): The ID of the data field.
            size (int): The size of the data.
            path (str): The path of the data.
            relation (str): The relation of the data.
            location (int): The location of the data.
            parity (bool): The parity flag of the data.
        """
        super().__init__()
        data_field = self.fetch((Data.GET_FIELD_QUERY, (id_num,)))
        self.hash_value = data_field[0]
        self.id_num = id_num
        self.size = data_field[2]
        self.path = data_field[3]
        self.relation = data_field[4]
        self.location = data_field[5]
        self.parity = False if data_field[6] == 0 else True

    @staticmethod
    def CreateField(path: str, user_id: str, drive: int, file_hash: bytes, size: int, parity: bool = False):
        """
        Static method to create a data field with path information.

        Args:
            path (str): The path of the data.
            user_id (str): The user ID associated with the data.
            drive (int): The drive ID associated with the data.
            file_hash (bytes): The hash value of the data.
            size (int): The size of the data.
            parity (bool): The parity flag of the data (optional, default is False).

        Returns:
            Data: A Data object representing the created data field.
        """
        db_session = DataBaseSession()
        parity = 0 if not parity else 1
        db_session.insert(Data.INSERT_FILED, (file_hash, size, user_id, path, drive, parity))
        rec_id = Data._get_latest_record_id()
        return Data(rec_id)

    @staticmethod
    def CreateFieldNoPath(user_id: str, drive: int, file_hash: bytes, size: int, parity: bool = False):
        """
        Static method to create a data field without path information.

        Args:
            user_id (str): The user ID associated with the data.
            drive (int): The drive ID associated with the data.
            file_hash (bytes): The hash value of the data.
            size (int): The size of the data.
            parity (bool): The parity flag of the data (optional, default is False).

        Returns:
            Data: A Data object representing the created data field.
        """
        db_session = DataBaseSession()
        parity = 0 if not parity else 1
        db_session.insert(Data.INSERT_FILED_NOT_PATH, (file_hash, size, user_id, drive, parity))
        rec_id = Data._get_latest_record_id()
        return Data(rec_id)

    @staticmethod
    def update_path_filed(id: int, path: str):
        """
        Static method to update the path of a data field.

        Args:
            id (int): The ID of the data field.
            path (str): The new path of the data.
        """
        db_session = DataBaseSession()
        db_session.insert(Data.UPDATE_PATH_FILED, (path, id))

    @staticmethod
    def get_data_records():
        """
        Static method to retrieve all data records.

        Returns:
            list: A list of tuples representing data records.
        """
        db_session = DataBaseSession()
        res = db_session.fetch(Data.GET_RECORDS, all=True)
        return res

    @staticmethod
    def _get_latest_record_id():
        """
        Static method to retrieve the latest record ID.

        Returns:
            int: The latest record ID.
        """
        db_session = DataBaseSession()
        query = 'SELECT MAX(id) FROM Data'
        id_num = db_session.fetch(query)
        return id_num[0]

    def _get_file_data(self, file_path):
        """
        Method to retrieve data from a file.

        Args:
            file_path (str): The path of the file.

        Returns:
            bytes: The data read from the file.
        """
        file_path = Path(file_path)
        with open(file_path, 'rb') as file:
            return file.read()

    @staticmethod
    def update_size_by_hash_path_relation(size: int, path: str, drive_id: int, relation: str):
        """
        Static method to update the size of a data field based on hash, path, and relation.

        Args:
            size (int): The size to be updated.
            path (str): The path of the data.
            drive_id (int): The drive ID associated with the data.
            relation (str): The relation of the data.
        """
        db_session = DataBaseSession()
        db_session.insert(Data.UPDATE_SIZE_BY_HASH_PATH_RELATION, (size, drive_id, path, relation))
        del db_session

    @staticmethod
    def get_drive_used_size(drive_id: int):
        """
        Static method to retrieve the used size of a drive.

        Args:
            drive_id (int): The ID of the drive.

        Returns:
            int: The used size of the drive.
        """
        db_session = DataBaseSession()
        used_size = db_session.fetch((Data.GET_DRIVE_USED_SIZE, (drive_id,)))[0]
        return 0 if used_size is None else int(used_size)

    @staticmethod
    def get_all_drives_ids():
        db_session = DataBaseSession()
        ids = db_session.fetch(Data.DRIVES_IDS,all=True)
        return [n_id[0] for n_id in ids]

    @staticmethod
    def get_data_crossing(user_id: str):
        db_session = DataBaseSession()
        res = db_session.fetch((Data.DATA_CROSSING,(user_id,)),all=True)
        return {mac:int(total) for mac, total in res}
    
    @staticmethod
    def get_actual_data_sum():
        db_session = DataBaseSession()
        res = db_session.fetch(Data.ACTUAL_DATA_SUM)[0]
        if res is None: return 0
        return int(res)
    
    @staticmethod
    def get_recoverd_data_sum():
        db_session = DataBaseSession()
        res = db_session.fetch(Data.RECOVERD_DATA_COUNT)[0]
        if res is None: return 0
        return int(res)
    
    @staticmethod
    def check_if_drive_used_for_data(drive_id:int):
        db_session = DataBaseSession()
        res = db_session.fetch((Data.CHECK_IF_DRIVE_USED_FOR_DATA,(drive_id,)))[0]
        return True if res==1 else False
    
    @staticmethod
    def get_file_records(drive_id:int):
        db_session = DataBaseSession()
        res = db_session.fetch((Data.GET_FILE_RECORDS_FOR_DRIVE,(drive_id,)),all=True)
        return res
    
if __name__ == "__main__":
    print(Data.get_file_records(119))




