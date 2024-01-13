import mysql.connector
import mysql.connector.errors as data_errors
from random import randbytes, randint
from hashlib import sha256
# mydb = 

class User:
    def __init__(self, full_name: str,user_id: str,password:str):
        
        self.conn, self.cursor = self._get_connector()
        #TODO: type checks
        hashed_pass, salt = self._generate_pass(password.encode())
        AES_key = self._generate_AES_key()
        query = 'INSERT INTO `data_users` VALUES (%s, %s ,%s, %s, %s)'
        values = (user_id, full_name, hashed_pass,AES_key, salt)
        try:
            self.cursor.execute(query,values)
            self.conn.commit()
            self.full_name = full_name
            self.user_name = user_id
            self.password = hashed_pass
            self.AES_key = AES_key
            self.salt = salt
        except data_errors.IntegrityError as err:
            print(err)
    
    # @classmethod
    # def signin(cls, user_id: str, password:str):
    #     return

    def _get_salt(self, user_id:str):
        qury = 'select (salt) from data_users where user_id = %s'
        values= (user_id)
        res = self.cursor.fetchall(qury, values)
        print(res)

    def _generate_pass(self, plain_text:bytes):
        SALT_RANGE = (1,10**10)
        salt = randint(SALT_RANGE[0],SALT_RANGE[1])
        return sha256(str(salt).encode() + plain_text).hexdigest(), salt



    def _generate_AES_key(self, key_size = 128, bytes_size = 100):
        full_key = ''
        hash_byte_size = 32
        for i in range(key_size//hash_byte_size):
            key = randbytes(bytes_size)
            full_key += sha256(key).hexdigest()
        return full_key
    
    def _get_connector(address = 'localhost',user_name = 'ariel', password='112358'):
        conn = mysql.connector.connect(
            host="localhost",
            user="ariel",
            password="112358",
            database ='RAID'
        )
        cursor = conn.cursor()
        return conn, cursor

# print(mydb) 
# print(len(User._generate_AES_key()))
# user = User('ariel cohen', 'ariel1d2dd4', '1212')
# user = User('asdasd','asdasd')
SALT_RANGE = (1,10**10)
cnt = 0
for i in range(100):
    salt = randint(SALT_RANGE[0],SALT_RANGE[1])
    if (len(str(salt))>=11):
        cnt+=1
print(cnt)