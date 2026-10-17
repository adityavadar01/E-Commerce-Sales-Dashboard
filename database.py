import mysql.connector


def connect_database():

    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Rahul123@",
        database="ganesh_nashta"
    )

    return connection


try:

    db = connect_database()

    print("Database connected successfully!")

    db.close()

except mysql.connector.Error as error:

    print("Database connection failed!")
    print(error)