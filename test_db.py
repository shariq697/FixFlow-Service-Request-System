import pymysql

try:
    con = pymysql.connect(
        host="52.90.36.247",
        user="fixuser",
        password="password123",
        db="fixflow"
    )

    print("CONNECTED SUCCESSFULLY")

    con.close()

except Exception as e:
    print("ERROR:", e)
