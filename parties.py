"""
This class manages the relationship between real drives and parity drives in a database.

Attributes:
    CREATE_FIELD (str): SQL query to create a new field in the parties table.
    CONNECTED_DRIVES_TO_REAL_DRIVE (str): SQL query to get connected drives to a real drive.
    IF_DRIVE_CONNECTED_TO_PARITY (str): SQL query to check if a drive is connected to a parity drive.

Methods:
    create_field: Static method to create a new field in the parties table.
    connect_drives_to_parity: Static method to connect drives to a parity drive.
    get_drives_connected_to_drive: Static method to get drives connected to a specified drive.
    is_connected_to_parity: Static method to check if a drive is connected to a parity drive.
"""

from DataBaseSession import DataBaseSession
from server_Exceptions import NotConnectedToPartiyDrive
class Parties(DataBaseSession):
    CREATE_FIELD = 'INSERT INTO parties (real_drive_id, parity_drive_id) VALUES (%s, %s)'
    CONNECTED_DRIVES_TO_REAL_DRIVE = """select real_drive_id as 'real', location as 'parity'
                                        FROM raid.parties AS parties, raid.data AS data_table
                                        WHERE data_parity_drive_record_id = 
                                                                            (
                                                                            SELECT data_parity_drive_record_id
                                                                            FROM raid.parties
                                                                            WHERE real_drive_id=%s
                                                                            )
                                        AND data_table.id = parties.data_parity_drive_record_id
                                        AND real_drive_id !=%s """
    CONNECTED_DRIVES_TO_PARITY_DRIVE = "SELECT * FROM raid.parties WHERE parity_drive_id=%s"
    IF_DRIVE_CONNECTED_TO_PARITY = "SELECT * from parties WHERE real_drive_id=%s"
    GET_CONNECTED_DRIVES = """
                            select parity_drive_id 'parity', NULL 'real'
                            from parties
                            where real_drive_id=%s
                            UNION
                            SELECT ' ', real_drive_id 'real'
                            FROM parties
                            WHERE parity_drive_id IN
                            (
                                SELECT parity_drive_id
                                FROM parties 
                                WHERE real_drive_id=%s
                            ) AND real_drive_id !=%s
                            """
    CHECK_IF_EVEN_CONNECTED ="""SELECT 
                                EXISTS(
                                SELECT *
                                from parties
                                where parity_drive_id=%s OR real_drive_id=%s
                                )"""
    CHECK_IF_PARITY_DRIVE = """
                            SELECT
                            EXISTS(
                            select * from parties where parity_drive_id=%s)
                            """
    @staticmethod
    def create_field(real_drive_id, data_parity_drive_record_id):
        """
        Static method to create a new field in the parties table.

        Args:
            real_drive_id (int): The ID of the real drive.
            data_parity_drive_record_id (int): The ID of the parity drive record.
        """
        db = DataBaseSession()
        db.insert(Parties.CREATE_FIELD, (real_drive_id, data_parity_drive_record_id))
        del db
    
    @staticmethod
    def connect_drives_to_parity(used_drives: list, parity_drive_id: int):
        """
        Static method to connect drives to a parity drive.

        Args:
            real_drives_list (list): List of real drive IDs.
            data_parity_id (int): The ID of the parity drive.
        
        Raises:
            TypeError: If real_drives_list is not a list.
        """
        if not isinstance(used_drives, list):
            raise TypeError(f"expected real_drives_list to be list got {type(used_drives)}")
        
        for real_drive_id in used_drives:
            Parties.create_field(real_drive_id, parity_drive_id)
    
    @staticmethod
    def get_drives_connected_to_drive(parity_drive_id: int):
        """
        Static method to get drives connected to a specified drive.

        Args:
            drive_id (int): The ID of the drive.

        Returns:
            tuple: A tuple containing the IDs of connected drives and the ID of the parity drive.
        """
        db = DataBaseSession()
        records = db.fetch((Parties.CONNECTED_DRIVES_TO_PARITY_DRIVE, (parity_drive_id, parity_drive_id)), all=True)
        if records !=[]:
            return tuple([record[0] for record in records]), records[0][1]
        raise NotConnectedToPartiyDrive()
    
    @staticmethod
    def is_connected_to_parity(drive_id: int):
        """
        Static method to check if a drive is connected to a parity drive.

        Args:
            drive_id (int): The ID of the drive.

        Returns:
            bool: True if connected to a parity drive, False otherwise.
        """
        db = DataBaseSession()
        return False if db.fetch((Parties.IF_DRIVE_CONNECTED_TO_PARITY, (drive_id,))) is None else True

    @staticmethod
    def get_connected_drives_to_real(real_id:int):
        db = DataBaseSession()
        ans = db.fetch((Parties.GET_CONNECTED_DRIVES, (real_id,real_id,real_id)),all=True)
        print(ans)
        if len(ans)==0:
            return None
        return int(ans[1][1]), int(ans[0][0])
    
    @staticmethod
    def check_if_connected(drive_id:int):
        db = DataBaseSession()
        ans = db.fetch((Parties.CHECK_IF_EVEN_CONNECTED, (drive_id, drive_id)))[0]
        return True if ans==1 else False
    
    @staticmethod
    def check_if_parity_drive(drive_id:int):
        db = DataBaseSession()
        ans = db.fetch((Parties.CHECK_IF_PARITY_DRIVE,(drive_id,)))[0]
        return False if ans==0 else True
    
    


if __name__ == '__main__':
    print(Parties.get_connected_drives_to_real(119))
