"""
This class represents a user in the system.

Attributes:
    get_AES_KEY_WITH_ID (str): SQL query to retrieve AES key based on user ID.
    
Methods:
    __init__: Constructor method to initialize a User object.
    _get_salt: Internal method to retrieve salt for a given user ID.
    _generate_pass: Internal method to generate hashed password and salt.
    _create_password: Internal method to create a hashed password.
    _generate_AES_key: Internal method to generate an AES key.
    get_AES_key_by_id: Static method to retrieve AES key based on user ID.

"""
import mysql.connector
import mysql.connector.errors as data_errors
from gui_Exceptions import *
from random import randbytes, randint
from hashlib import sha256
import sys
sys.path.append('E:/YUDB/project/RAID-Store')
from DataBaseSession import DataBaseSession
# mydb = 

class User(DataBaseSession):
    get_AES_KEY_WITH_ID = "select AES_Key from data_users where user_id=%s;"
    CHECK_IF_USERS_EXSISTS = 'select exists(select * from data_users)'  
    CHANGE_PASSWORD = "UPDATE `raid`.`data_users` SET `password` = %s, `salt` = %s WHERE `user_id` = %s;"
    def __init__(self,user_id: str,password:str, full_name: str ='', sign_in:bool = False):
        """
        Constructor method to initialize a User object.

        Args:
            user_id (str): The user's ID.
            password (str): The user's password.
            full_name (str): The user's full name (optional, default is '').
            sign_in (bool): Flag indicating whether the user is signing in (optional, default is False).
        
        Raises:
            WrongPassword: If the provided password is incorrect.
            UserNotExist: If the user does not exist in the database.
        """
        super().__init__()
        #TODO: type checks
        if not sign_in:
            hashed_pass, salt = self._generate_pass(password.encode())
            AES_key = self._generate_AES_key()
            query = 'INSERT INTO `data_users` VALUES (%s, %s ,%s, %s, %s)'
            values = (user_id, full_name, hashed_pass,AES_key, salt)
            self.insert(query, values)
        else:
            salt = self._get_salt(user_id)
            hashed_password = self._create_password(salt,password)
            query = 'SELECT * FROM data_users WHERE password = %s AND user_id = %s'
            values = (hashed_password, user_id)
            user = self.fetch((query,values))
            if user is not None:
                full_name = user[1]
                hashed_pass = user[2]
                AES_key = user[3]
                salt = user[4]
            else: 
                raise WrongPassword('WRONG PASSWORD!')

        try:
            self.full_name = full_name
            self.user_name = user_id
            self.password = password
            self.AES_key = AES_key
            self.salt = salt
        except data_errors.IntegrityError as err:
            print(err)


    def _get_salt(self, user_id:str):
        """
        Retrieve salt for a given user ID.

        Args:
            user_id (str): The user's ID.

        Returns:
            int: The salt value.

        Raises:
            UserNotExist: If the user does not exist in the database.
        """
        qury = 'select (salt) from data_users where user_id=%s'
        values= (user_id,)
        res = self.fetch((qury,values), all=False)
        if res is None:
            raise UserNotExist(f'the user {user_id} is not exsit')
        return res[0]

    def _generate_pass(self, plain_text:bytes):
        """
        Generate hashed password and salt.

        Args:
            plain_text (bytes): The plaintext password.

        Returns:
            tuple: A tuple containing the hashed password and the salt.
        """
        SALT_RANGE = (1,10**9)
        salt = randint(SALT_RANGE[0],SALT_RANGE[1])
        return sha256(str(salt).encode() + plain_text).hexdigest(), salt

    def _create_password(self, salt:int, password:str):
        """
        Create a hashed password.

        Args:
            salt (int): The salt value.
            password (str): The plaintext password.

        Returns:
            str: The hashed password.
        """
        return sha256(str(salt).encode() + password.encode()).hexdigest()

    def _generate_AES_key(self, key_size = 128, bytes_size = 100):
        """
        Generate an AES key.

        Args:
            key_size (int): The size of the key in bits (optional, default is 128).
            bytes_size (int): The size of the key in bytes (optional, default is 100).

        Returns:
            str: The generated AES key.
        """
        full_key = ''
        hash_byte_size = 32
        for i in range(key_size//hash_byte_size):
            key = randbytes(bytes_size)
            full_key += sha256(key).hexdigest()
        return full_key

    def change_password(self, new_password:str):
        hashed_pass, salt = self._generate_pass(new_password.encode())
        self.insert(User.CHANGE_PASSWORD,(hashed_pass,salt,self.user_name))

    @staticmethod
    def get_AES_key_by_id(id: str):
        """
        Retrieve AES key based on user ID.

        Args:
            id (str): The user's ID.

        Returns:
            str: The AES key.
        """
        db = DataBaseSession()
        key = db.fetch((User.get_AES_KEY_WITH_ID,(id,)))[0]
        del db
        return key

    @staticmethod
    def check_if_users_exsists():
        db = DataBaseSession()
        res = db.fetch(User.CHECK_IF_USERS_EXSISTS)[0]
        return True if res==1 else False

  
if __name__ == "__main__":
    user = User('ariel0','1234',sign_in=True)
    user.change_password('123')