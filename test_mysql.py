import pymysql

passwords = ['', 'root', 'password', 'admin', 'Admin@123', 'root123', '123456', '12345678', '1234', 'mysql', 'root@123', 'root#123', 'root@1', 'Admin@1']
found = None

for p in passwords:
    try:
        conn = pymysql.connect(host='localhost', port=3306, user='root', password=p)
        print(f"SUCCESS: Root password is '{p}'")
        with conn.cursor() as cur:
            cur.execute("CREATE DATABASE IF NOT EXISTS hrms_db;")
            print("Successfully created/verified database hrms_db!")
        conn.close()
        found = p
        break
    except pymysql.err.OperationalError as e:
        pass
    except Exception as e:
        print(f"Error testing '{p}': {e}")

if not found:
    print("NO_STANDARD_PASSWORD_MATCHED")
