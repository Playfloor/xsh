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

    def select(self, alias='', select=None, where=None, limit=None, offset=None): 
        sql = '' 
        if select == None:
            sql = 'select * from @{0}@'.format(self.alias) 
        else:
            sql = 'select {0} from @{1}@'.format(select, self.alias)

        if where != None:
            sql = sql + " where " + where

        if limit != None:
            sql = sql + " limit {0}".format(limit)

        if offset != None:
            sql = sql + " offset {0}".format(offset) 

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

    def explain(self, analyze=False, format='json'):
        self.build_sql()
        opt = ''
        if format == 'json': 
            if analyze:
                opt = '(format json, analyze)'
            else:
                opt = '(format json)' 
        else:
            if analyze:
                opt = '(analyze)' 
        expsql = 'explain {0} {1}'.format(opt, self.sql)
        cols, rows = self.conn.execute(expsql)
        return rows[0][0]

    def dotplan(self, fn, analyze=False):
        exp = self.explain(analyze=analyze)
        dp = xpg.xtplot.DotPlan(exp)
        dp.render(fn)

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

    def barchart(self, ylabel=None):
        cols, rows = self.execute()
        lc = xpg.xtplot.BarChart(ylabel)
        for row in rows:
            lc.addx(row[0])
            for c in range(1, len(cols)):
                # print("adding ", cols[c], row[c])
                lc.add(cols[c], row[c])
        lc.draw()

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

def fromArray(conn, tups, alias="", colnames = None):
    if tups is None or len(tups) == 0:
        raise Exception("xtable from python array must have at least one row.")
    cur = conn.cursor()
    mstr = '(' + ','.join(['%s' for r in tups[0]]) + ')'
    vstr = 'VALUES ' + ','.join([cur.mogrify(mstr, row).decode('utf-8') for row in tups])
    conn.close_cursor(cur)
    if colnames is None:
        return fromSQL(conn, vstr, alias=alias) 
    else:
        vt = fromSQL(conn, vstr)
        sel = ','.join(['column' + str(i+1) + ' as ' + colnames[i] for i in range(len(colnames))])
        return vt.select(alias=alias, select=sel)

if __name__ == '__main__':
    import xpg.conn
    c1 = xpg.conn.Conn("ftian", database="ftian") 
    t1 = fromTable(c1, "t")
    t2 = fromSQL(c1, "select i from generate_series(1, 10) i", alias="t2")
    t3 = fromQuery(c1, "select j from @t@ limit 10", alias="t3") 

    # print(t2.show())
    # print(t3.show())

    t4 = fromQuery(c1, "select * from @t2@, @t3@ where @t2.i@ = @t3.j@") 
    t4.dotplan("/tmp/exp")
    t4.dotplan("/tmp/expa", analyze=True)

    # tups = [(1, 2, 'ok'), (3, 4, 'ok2')]
    # t5 = fromArray(c1, tups) 
    # print(t5.show())
    # t6 = fromArray(c1, tups, alias='tups', colnames=['i', 'j', 'k'])
    # print(t6.show())

    t5 = fromSQL(c1, "select 'i' || (i%10) as k, sum(i) as si, sum(j) as sj from t group by (i%10)") 
    t5.barchart()
    plt.savefig('/tmp/xtable.png')

    # t6 = fromQuery(c1, "select 'i', sum(i) from @t@ union all select 'j', sum(j) from @t@")
    # print(t6.show())
    # t6.piechart()

