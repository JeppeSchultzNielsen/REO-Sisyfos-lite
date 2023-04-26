import numpy as np

class ResultsFile:
    def __init__(self, name: str):
        self.name = name
        f = open(name,"r") 
        self.header = f.readline()
        self.splitted = self.header.split()
        self.data = np.transpose(np.loadtxt(name, skiprows = 1))

    def getColumn(self,toGet):
        ind = self.splitted.index(toGet)
        return self.data[ind]