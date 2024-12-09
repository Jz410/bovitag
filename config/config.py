import os

class Config:
    SECRET_KEY = os.urandom(24)
    DB_CONFIG = {
        'host': "bbgtlqffrhru20mqjx0c-mysql.services.clever-cloud.com",
        'user': "uf7vsfgxsseneyqb",
        'password': "t0kvNi2jGemkaULxm5jc",
        'database': "bbgtlqffrhru20mqjx0c",
        'cursorclass': 'DictCursor'
    }