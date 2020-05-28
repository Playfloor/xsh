import tabulate
import xpg.xtplot
import matplotlib.pyplot as plt

class XCol:
    def __init__(self, n, t):
        self.name = n
        self.type = t

class XTable:
    def __init__(self, c, origsql="", alias=""): 
        self.conn = c
        self.origsql = origsql
        self.sql = None 
        if alias == "":
            self.alias = c.next_tmpname()
        else:
            self.alias = alias 
        self.inputs = {}

    # resolve a column.  
    # @x.y@ where x is a number, y is colname -> tablealias.colname
    def resolve_col(self, s):
        strs = s.split('@')
        rs = []
        i = 0
        while i < len(strs):
            rs.append(strs[i])
            i += 1 

            if i == len(strs):
                break

            if strs[i] == '':
                rs.append('@')
            else:
                # record alias table.
                xy = strs[i].split('.')
                self.inputs[xy[0]] = 1
                rs.append(strs[i])
            i += 1 
        # print(rs)
        return "".join(rs)

    def build_sql(self): 
        if self.sql != None:
            return
        rsql = self.resolve_col(self.origsql)
        if self.inputs == None or len(self.inputs) == 0:
            self.sql = rsql
        else:
            self.sql = "WITH "
            self.sql += ",\n".join([xtn + " as (" + self.conn.getxt(xtn).sql + ")" for xtn in self.inputs])
            self.sql += "\n"
            self.sql += rsql

    def select(self, alias='', select=None, where=None, limit=None, samplerows=None, samplepercent=None): 
        sql = '' 
        if select == None:
            sql = 'select * from @{0}@'.format(self.alias) 
        else:
            sql = 'select {0} from @{1}@'.format(select, self.alias)

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

        ret = XTable(self.conn, sql, alias) 
        ret.build_sql()
        self.conn.xts[ret.alias] = ret 
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

    def linechart(self, xlabel='x', ylabel='y'):
        cols, rows = self.execute()
        lc = xpg.xtplot.LineChart(xlabel, ylabel)
        for row in rows:
            for c in range(len(cols)):
                lc.add(cols[c], row[c])
        lc.draw()

    def xlinechart(self, xlabel='x', ylabel='y'):
        cols, rows = self.execute()
        lc = xpg.xtplot.LineChart(xlabel, ylabel)
        for row in rows:
            lc.addx(row[0])
            for c in range(1, len(cols)):
                # print("adding ", cols[c], row[c])
                lc.add(cols[c], row[c])
        lc.draw()

    def piechart(self):
        _, rows = self.execute()
        lbls = [r[0] for r in rows]
        vals = [r[1] for r in rows]
        pc = xpg.xtplot.PieChart(vals, labels=lbls)
        pc.draw()


def fromQuery(conn, qry, alias=""):
    xt = XTable(conn, qry, alias) 
    xt.build_sql()
    conn.xts[xt.alias] = xt
    return xt

def fromSQL(conn, sql, alias=""):
    xt = XTable(conn, sql, alias) 
    xt.sql = xt.origsql
    conn.xts[xt.alias] = xt
    return xt

def fromTable(conn, tn, alias=""):
    if alias == "":
        alias = tn
    return fromSQL(conn, "select * from " + tn, alias)

if __name__ == '__main__':
    import xpg.conn
    c1 = xpg.conn.Conn("ftian", database="ftian") 
    t1 = fromTable(c1, "t")
    t2 = fromSQL(c1, "select i from generate_series(1, 10) i", alias="t2")
    t3 = fromQuery(c1, "select j from @t@ limit 10", alias="t3") 

    print(t2.show())
    print(t3.show())

    t4 = fromQuery(c1, "select * from @t2@, @t3@ where @t2.i@ = @t3.j@") 
    print(t4.show())

    t5 = t1.select(select='i, j')
    t5.xlinechart()
    plt.show()

    # t6 = fromQuery(c1, "select 'i', sum(i) from @t@ union all select 'j', sum(j) from @t@")
    # print(t6.show())
    # t6.piechart()

