import psycopg2

try:
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="postgres",  # Yahan apna password likh dena (agar postgres hai toh yeh hi rehne dein)
        host="localhost",
        port="5432"
    )
    print("Connection Successful!")
    conn.close()
except Exception as e:
    print("Error:", e)
