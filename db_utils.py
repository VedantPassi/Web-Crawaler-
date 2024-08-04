import pymysql

def create_database_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='82461937Cr7@',
        db='words',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
