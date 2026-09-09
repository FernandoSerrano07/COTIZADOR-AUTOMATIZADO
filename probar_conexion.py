import pymysql

try:
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='seguridad_y_redes',
        port=3306
    )
    print("¡Conexión exitosa a MySQL en XAMPP!")
    connection.close()
except Exception as e:
    print(f"Error al conectar: {e}")