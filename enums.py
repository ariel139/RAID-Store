from enum import Enum
import server_Exceptions

server_exceptions ={
    '0': server_Exceptions.UnknownError,
    '1': server_Exceptions.UserDoesNotExsit,
    '2': server_Exceptions.UserAlreadyExsit,
    '3': server_Exceptions.InValidMessageFormat,
    '6': server_Exceptions.DeviceAlreadyExsits
}

class DriveTypes(Enum):
    SCSI='1'
    HDC='2'
    IDE='3'
    USB='4'
    _1394 ='5'
    Null = '6'
    
drive_types = {
    'SCSI' :DriveTypes.SCSI,
    'HDC': DriveTypes.HDC,
    'IDE': DriveTypes.IDE,
    'USB': DriveTypes.USB,
    '1394': DriveTypes._1394
}
class FileSystems(Enum):
    NTFS = '1'
    FAT = '2'
    exFAT = '3'
    ReFS = '4'
    UDF = '5'
    CDFS = '6'
    DFS = '7'

file_systems = {
    'NTFS' : FileSystems.NTFS,
    'ReFS' : FileSystems.ReFS,
    'exFAT' : FileSystems.exFAT,
    'CDFS' : FileSystems.CDFS,
    'FAT' : FileSystems.FAT,
    'UDF' : FileSystems.UDF,
    'DFS' : FileSystems.DFS,
}
class Category(Enum):
    Authentication=1
    Storage = 2
    Recovering = 3
    Errors = 4
    Status = 5
client_blocking_messages={
    Category.Recovering: [7,9],
    Category.Authentication:[],
    Category.Errors : [],
    Category.Status: [],
    Category.Storage: [],

}
class Requests(Enum):
    Add=1
    Retrive=2
    Delete=3


client_out_puts = {
    Category.Authentication.name :{
        '4': 'signed in succefuly',
        '5': 'You signed up succcesfuly!',
        '6': 'You deleted your PC succefuly. exting...',
        
    },
    Category.Storage.name :{
        '6':'You added stroge space succefuly',
        '8':'You added a drive succesfly'
    },
    Category.Status.name:{
        '3': 'turn off complete'
    }
    
}


class Countries(Enum):
    Afghanistan= 1,
    Albania= 2,
    Algeria= 3,
    Andorra= 4,
    Angola= 5,
    Antigua_and_Barbuda= 6,
    Argentina= 7,
    Armenia= 8,
    Australia= 9,
    Austria= 10,
    Azerbaijan= 11,
    Bahamas= 12,
    Bahrain= 13,
    Bangladesh= 14,
    Barbados= 15,
    Belarus= 16,
    Belgium= 17,
    Belize= 18,
    Benin= 19,
    Bhutan= 20,
    Bolivia= 21,
    Bosnia_and_Herzegovina= 22,
    Botswana= 23,
    Brazil= 24,
    Brunei_Darussalam= 25,
    Bulgaria= 26,
    Burkina_Faso= 27,
    Burundi= 28,
    Cambodia= 29,
    Cameroon= 30,
    Canada= 31,
    Cape_Verde= 32,
    Central_African_Republic= 33,
    Chad= 34,
    Chile= 35,
    China= 36,
    Colombia= 37,
    Comoros= 38,
    Congo= 39,
    Democratic_Republic_of_the_Congo= 40,
    Costa_Rica= 41,
    Côte_dIvoire= 42,
    Croatia= 43,
    Cuba= 44,
    Cyprus= 45,
    Czech_Republic= 46,
    Denmark= 47,
    Djibouti= 48,
    Dominica= 49,
    Dominican_Republic= 50,
    East_Timor= 51,
    Ecuador= 52,
    Egypt= 53,
    El_Salvador= 54,
    Equatorial_Guinea= 55,
    Eritrea= 56,
    Estonia= 57,
    Eswatini= 58,
    Ethiopia= 59,
    Fiji= 60,
    Finland= 61,
    France= 62,
    Gabon= 63,
    Gambia= 64,
    Georgia= 65,
    Germany= 66,
    Ghana= 67,
    Greece= 68,
    Grenada= 69,
    Guatemala= 70,
    Guinea= 71,
    Guinea_Bissau= 72,
    Guyana= 73,
    Haiti= 74,
    Honduras= 75,
    Hungary= 76,
    Iceland= 77,
    India= 78,
    Indonesia= 79,
    Iran= 80,
    Iraq= 81,
    Ireland= 82,
    Israel= 83,
    Italy= 84,
    Jamaica= 85,
    Japan= 86,
    Jordan= 87,
    Kazakhstan= 88,
    Kenya= 89,
    Kiribati= 90,
    North_Korea= 91,
    South_Korea= 92,
    Kosovo= 93,
    Kuwait= 94,
    Kyrgyzstan= 95,
    Laos= 96,
    Latvia= 97,
    Lebanon= 98,
    Lesotho= 99,
    Liberia= 100,
    Libya= 101,
    Liechtenstein= 102,
    Lithuania= 103,
    Luxembourg= 104,
    Madagascar= 105,
    Malawi= 106,
    Malaysia= 107,
    Maldives= 108,
    Mali= 109,
    Malta= 110,
    Marshall_Islands= 111,
    Mauritania= 112,
    Mauritius= 113,
    Mexico= 114,
    Micronesia= 115,
    Moldova= 116,
    Monaco= 117,
    Mongolia= 118,
    Montenegro= 119,
    Morocco= 120,
    Mozambique= 121,
    Myanmar= 122,
    Namibia= 123,
    Nauru= 124,
    Nepal= 125,
    Netherlands= 126,
    New_Zealand= 127,
    Nicaragua= 128,
    Niger= 129,
    Nigeria= 130,
    North_Macedonia= 131,
    Norway= 132,
    Oman= 133,
    Pakistan= 134,
    Palau= 135,
    Panama= 136,
    Papua_New_Guinea= 137,
    Paraguay= 138,
    Peru= 139,
    Philippines= 140,
    Poland= 141,
    Portugal= 142,
    Qatar= 143,
    Romania= 144,
    Russia= 145,
    Rwanda= 146,
    Saint_Kitts_and_Nevis= 147,
    Saint_Lucia= 148,
    Saint_Vincent_and_the_Grenadines= 149,
    Samoa= 150,
    San_Marino= 151,
    São_Tomé_and_Príncipe= 152,
    Saudi_Arabia= 153,
    Senegal= 154,
    Serbia= 155,
    Seychelles= 156,
    Sierra_Leone= 157,
    Singapore= 158,
    Slovakia= 159,
    Slovenia= 160,
    Solomon_Islands= 161,
    Somalia= 162,
    South_Africa= 163,
    South_Sudan= 164,
    Spain= 165,
    Sri_Lanka= 166,
    Sudan= 167,
    Suriname= 168,
    Sweden= 169,
    Switzerland= 170,
    Syria= 171,
    Tajikistan= 172,
    Tanzania= 173,
    Thailand= 174,
    Togo= 175,
    Tonga= 176,
    Trinidad_and_Tobago= 177,
    Tunisia= 178,
    Turkey= 179,
    Turkmenistan= 180,
    Tuvalu= 181,
    Uganda= 182,
    Ukraine= 183,
    United_Arab_Emirates= 184,
    United_Kingdom= 185,
    United_States_of_America= 186,
    Uruguay= 187,
    Uzbekistan= 188,
    Vanuatu= 189,
    Venezuela= 190,
    Vietnam= 191,
    Yemen= 192,
    Zambia= 193,
    Zimbabwe= 194
