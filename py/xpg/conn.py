import psycopg2
import os
# import pg8000

class Conn:
    def __init__(self, user=None, host='localhost', port=5432, database=None, password=None):
        if user is None:
            user = os.environ['USER']
        if database is None:
            database = user
        # self.conn = pg8000.connect(user, host=host, port=port, database=database, password=password) 
        constr = "dbname='{0}' user='{1}'".format(database, user)
        self.conn = psycopg2.connect(constr)
        self.nexttmp = 0
        # autocommit set to true by default.
        self.conn.autocommit = True
        self.xts = {}
   
    def rmxt(self, xt):
        del self.xts[xt]

    def getxt(self, xt):
        if xt in self.xts:
            return self.xts[xt]
        return None

    def close(self):
        self.conn.close()

    def next_tmpname(self):
        self.nexttmp += 1
        return "tmp_{0}".format(self.nexttmp)

    def execute(self, sql):
        cur = self.conn.cursor()
        cur.execute(sql) 
        # cols = [k[0].decode('ascii') for k in cur.description]
        cols = [k[0] for k in cur.description]
        rows = []
        while True:
            row = cur.fetchone()
            if row == None:
                break
            rows.append(row)
        cur.close()
        self.conn.commit()
        return cols, rows

    def execute_only(self, sql):
        cur = self.conn.cursor()
        cur.execute(sql) 
        cur.close()
        self.conn.commit()

    def cursor(self, sql=None):
        cur = self.conn.cursor()
        if sql is not None:
            cur.execute(sql) 
        return cur

    def close_cursor(self, cur):
        cur.close()
        self.conn.commit()
