import unittest
import sys, os

current_dir = os.path.dirname(os.path.abspath(__file__))
lower_directory_path = os.path.join(current_dir, 'C:/Users/ArielCohen/code/RAID-Store')
sys.path.append(lower_directory_path)
from DataBaseSession import DataBaseSession
db = DataBaseSession()
db.insert('INSERT INTO Computers (`MAC`, `size`, `geo_location`) VALUES (%s, %s, %s)',('0xccd9bc32d1f5',100,1))
print(db.fetch('SELECT *  FROM Computers '))
