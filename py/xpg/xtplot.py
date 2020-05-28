import matplotlib.pyplot as plt

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

