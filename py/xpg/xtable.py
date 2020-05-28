import tabulate

class XCol:
    def __init__(self, n, t):
        self.name = n
        self.type = t

class XTable:
    def __init__(self, c, origsql="", alias="", inputs=None):
        self.conn = c
        self.origsql = origsql
        self.sql = None 
        if alias == "":
            self.alias = c.next_tmpname()
        else:
            self.alias = alias 
        self.inputs = inputs

    def coldef(self, idx):
        return self.schema[idx]

    # resolve a column.  
    # #x.y# where x is a number, y is colname -> tablealias.colname
    def resolve_col(self, s):
        strs = s.split('#')
        rs = []
        i = 0

        while i < len(strs):
            rs.append(strs[i])
            i += 1 

            if i == len(strs):
                break

            if strs[i] == '':
                rs.append('#')
            else:
                xy = strs[i].split('.')
                if len(xy) == 1:
                    idx = int(xy[0])
                    rs.append(self.inputs[idx].alias)
                elif len(xy) == 2:
                    idx = int(xy[0])
                    tab = self.inputs[idx].alias
                    col = xy[1]
                    rs.append(tab + "." + col)
                else:
                    raise ValueError("sql place holder must be #x# or #x.y#")
            i += 1 
        return "".join(rs)

    def build_sql(self): 
        if self.sql != None:
            return

        rsql = self.resolve_col(self.origsql)
        if self.inputs == None or len(self.inputs) == 0:
            self.sql = rsql
        else:
            self.sql = "WITH "
            self.sql += ",\n".join([t.alias + " as (" + t.sql + ")" for t in self.inputs])
            self.sql += "\n"
            self.sql += rsql

    def select(self, alias='', select=None, where=None, limit=None, samplerows=None, samplepercent=None): 
        sql = '' 
        if select == None:
            sql = 'select * from #0#'
        else:
            sql = 'select {0} from #0#'.format(select)

        if where != None:
            sql = sql + " where " + where

        nlimit = 0
        if limit != None:
            nlimit += 1
            sql = sql + " limit {0}".format(limit)

        if samplerows != None:
            nlimit += 1
            sql = sql + " limit sample {0} rows".format(samplerows)

        if samplepercent != None:
            nlimit += 1
            sql = sql + " limit sample {0} percent".format(samplepercent)

        if nlimit > 1:
            raise ValueError("SQL Select can have at most one limit/sample clause")

        ret = XTable(self.conn, sql, alias, inputs=[self])
        return ret

    def cursor(self):
        self.build_sql()
        return self.conn.cursor(self.sql)

    def execute(self):
        self.build_sql()
        return self.conn.execute(self.sql) 

    def ctas(self, tablename, distributed_by=None):
        sql = "create table {0} as {1}".format(tablename, self.sql) 
        if distributed_by != None:
            sql += " distributed by ({0})".format(distributed_by)
        self.conn.execute_only(sql)

    def insert_into(self, tablename, cols=None):
        sql = "insert into {0} ".format(tablename)
        if cols != None:
            sep = '('
            for col in cols:
                sql += sep + col
            sql += ')'
        sql += self.sql
        self.conn.execute_only(sql)

    def show(self, tablefmt='psql'):
        cols, res = self.execute()
        return tabulate.tabulate(res, cols, tablefmt)


def fromQuery(conn, qry, alias="", inputs=None):
    xt = XTable(conn, qry, alias, inputs)
    return xt

def fromSQL(conn, sql, alias=""):
    xt = XTable(conn, sql, alias, None) 
    xt.sql = xt.origsql
    return xt

def fromTable(conn, tn, alias=""):
    return fromSQL(conn, "select * from " + tn, alias)

if __name__ == '__main__':
    import xpg.conn
    c1 = xpg.conn.Conn("ftian", database="ftian") 
    t1 = fromTable(c1, "t")
    t2 = fromSQL(c1, "select i from generate_series(1, 10) i")
    t3 = fromQuery(c1, "select j from #0# limit 10", inputs = [t1])

    print(t2.show())
    print(t3.show())

    t4 = fromQuery(c1, "select * from #0#, #1# where #0.i# = #1.j#", inputs=[t2, t3])
    print(t4.show())
