# import psycopg2
import os
import pg8000

class Conn:
    def __init__(self, user=None, host='localhost', port=5432, database=None, password=None):
        if user is None:
            user = os.environ['USER']
        self.conn = pg8000.connect(user, host=host, port=port, database=database, password=password) 
        self.nexttmp = 0
        # autocommit set to true by default.
        self.conn.autocommit = True
   
    def close(self):
        self.conn.close()

    def next_tmpname(self):
        self.nexttmp += 1
        return "tmp_{0}".format(self.nexttmp)

    def execute(self, sql):
        cur = self.conn.cursor()
        cur.execute(sql) 
        rows = cur.fetchall()
        cur.close()
        self.conn.commit()
        return rows

    def execute_only(self, sql):
        cur = self.conn.cursor()
        cur.execute(sql) 
        cur.close()
        self.conn.commit()

    def cursor(self, sql):
        cur = self.conn.cursor()
        cur.execute(sql) 
        return cur

