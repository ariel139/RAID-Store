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
    def __init__(self,user_id: str,password:str, full_name: str ='', sign_in:bool = False):
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
            self.password = hashed_pass
            self.AES_key = AES_key
            self.salt = salt
        except data_errors.IntegrityError as err:
            print(err)


    def _get_salt(self, user_id:str):
        qury = 'select (salt) from data_users where user_id=%s'
        values= (user_id,)
        res = self.fetch((qury,values), all=False)
        if res is None:
            raise UserNotExist(f'the user {user_id} is not exsit')
        return res[0]

    def _generate_pass(self, plain_text:bytes):
        SALT_RANGE = (1,10**9)
        salt = randint(SALT_RANGE[0],SALT_RANGE[1])
        return sha256(str(salt).encode() + plain_text).hexdigest(), salt

    def _create_password(self, salt:int, password:str):
        return sha256(str(salt).encode() + password.encode()).hexdigest()

    def _generate_AES_key(self, key_size = 128, bytes_size = 100):
        full_key = ''
        hash_byte_size = 32
        for i in range(key_size//hash_byte_size):
            key = randbytes(bytes_size)
            full_key += sha256(key).hexdigest()
        return full_key
  

# user = User('ariel0','1234','ariel cohen')
# SALT_RANGE = (1,10**10)
# cnt = 0
# for i in range(100):
#     salt = randint(SALT_RANGE[0],SALT_RANGE[1])
#     if (len(str(salt))>=11):
#         cnt+=1
# print(cnt)