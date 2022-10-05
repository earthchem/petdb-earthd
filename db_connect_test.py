import psycopg2
from config import config

def connect():
    """ Connect to the petDB database server """
    conn = None
    try:
        params = config()

        print('Connecting to the petDB database...')
        conn = psycopg2.connect(**params)
		
        cur = conn.cursor()
        
        print('Connected')
        cur.execute('SELECT version()')

        db_version = cur.fetchone()
        print(db_version)
              
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')


if __name__ == '__main__':
    connect()