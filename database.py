import pymysql

# Step 1: Database Connection Function
def create_database_connection():
    try:
        return pymysql.connect(
            host='localhost',  # Replace with your MySQL server address
            user='root',  # Replace with your MySQL username
            password='82461937Cr7@',  # Replace with your MySQL password
            db='words',  # Replace with your database name
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    except pymysql.MySQLError as e:
        print(f"Error connecting to the MySQL Database: {e}")
        return None

# Step 2: Insert Function
def insert_word(word):
    connection = create_database_connection()
    if connection is not None:
        try:
            with connection.cursor() as cursor:
                sql = "INSERT INTO words (word) VALUES (%s)"
                cursor.execute(sql, (word,))
            connection.commit()
        except Exception as e:
            print(f"Error while inserting into the database: {e}")
        finally:
            connection.close()