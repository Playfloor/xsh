
import matplotlib.pyplot as plt
import numpy as np
from graphviz import Digraph


class SeriesAccumulator:
    def __init__(self): 
        self.acc = {}

    def add(self, series, val):
        if series in self.acc:
            arr = self.acc[series]
        else:
            self.acc[series] = []
            arr = self.acc[series]

        arr.append(val)

class PieChart:
    def __init__(self, vals, labels=None):
        self.vals = vals
        self.labels = labels

    def draw(self):
        if self.labels == None:
            plt.pie(self.vals)
        else:
            plt.pie(self.vals, labels=self.labels)


class LineChart:
    def __init__(self, xlabel='x', ylabel='y', acc=None):
        self.fig, self.ax = plt.subplots(1, 1) 
        self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel(ylabel)
        self.x_start = 0
        self.x_inc = 1
        self.xvals = []

        if acc == None:
            self.acc = SeriesAccumulator()
        else:
            self.acc = acc

    def addx(self, x):
        self.xvals.append(x)

    def add(self, series, val):
        self.acc.add(series, val)

    def draw(self):
        if len(self.xvals) > 0:
            xaxis = self.xvals
        else:
            xaxis = None
        legend = []
        for series in self.acc.acc:
            vals = self.acc.acc[series]
            if xaxis == None:
                xaxis = [self.x_start + i * self.x_inc for i in range(len(vals))]
            # print("Draw ", series, " x: ", xaxis)
            # print("Draw ", series, " DATA: ", vals)
            self.ax.plot(xaxis, vals)
            legend.append(series)
        self.ax.legend(legend)
        self.fig.canvas.draw()

class BarChart:
    def __init__(self, ylabel=None, acc=None):
        self.xvals = []
        self.ylabel = ylabel
        if acc == None:
            self.acc = SeriesAccumulator()
        else:
            self.acc = acc

    def addx(self, x):
        self.xvals.append(x)

    def add(self, series, val):
        self.acc.add(series, val)

    def draw(self):
        fig, ax = plt.subplots(1, 1)
        if self.ylabel != None:
            self.ax.set_ylabel(ylabel)
        xs = np.arange(len(self.xvals))
        ax.set_xticks(xs)
        ax.set_xticklabels(self.xvals)

        legend = []
        series = list(self.acc.acc.keys())
        width = 0.5/len(series)

        for iseries in range(len(series)):
            srs = series[iseries]
            vals = self.acc.acc[srs]
            # print (xs, width, iseries)
            # print (vals)
            ax.bar(xs + (- 0.25 + width * iseries), vals, width, label=srs)
            legend.append(srs)
        ax.legend(legend)
        fig.canvas.draw()

class DotPlan: 
    def __init__(self, plan):
        self.plan = plan[0]['Plan']
        self.g = Digraph(format='png')
        self.cnt = 0
        self.build(self.plan)

    def nodeToStr(self, n): 
        # print (n)
        txt = n["Node Type"] 
        if "Relation Name" in n:
            txt += "\nRelation: " + n["Relation Name"]
        if "Alias" in n:
            txt += " (" + n["Alias"] + ")"
        if "Plan Rows" in n:
            txt += "\nPlan rows: " + str(n["Plan Rows"])
        if "Actual Rows" in n:
            txt += " Actual rows: " + str(n["Actual Rows"])
        return txt

    def build(self, n):
        nid = self.cnt
        self.cnt += 1

        self.g.node(str(nid), self.nodeToStr(n))
        if "Plans" in n:
            for c in n["Plans"]:
                cid = self.build(c)
                self.g.edge(str(nid), str(cid))
        return nid

    def dump(self):
        return self.g.source

    def render(self, fn):
        self.g.render(fn)

if __name__ == '__main__':
    import xpg.conn
    import xpg.xtable

    c1 = xpg.conn.Conn("ftian", database="ftian") 
    xt = xpg.xtable.fromQuery(c1, 'select count(*) from t t1, t t2 where t1.i = t2.j')
    exp = xt.explain()
    dp = DotPlan(exp)

    print(dp.dump())
    dp.render("/tmp/exp")

    

