import numpy as np
import sys
sys.path.append('../')
from PostProcessor import Node
from PostProcessor import PostProcessor

class ResultsFile:
    def __init__(self, name: str):
        self.name = name
        f = open(name,"r") 
        self.header = f.readline()
        self.splittedHeader = self.header.split()
        self.data = np.transpose(np.loadtxt(name, skiprows = 1))
        self.nodeNames = PostProcessor().names
        self.nodes = []
        for i in range(len(self.nodeNames)):
            self.nodes.append(Node(self.nodeNames[i]))
            self.nodes[i].readHeader(self.splittedHeader)

    def getColumn(self,toGet):
        if(isinstance(toGet,str)):
            ind = self.splittedHeader.index(toGet)
        else:
            ind = toGet
        return self.data[ind]
    
    def getNode(self,nodeName):
        ind = self.nodeNames.index(nodeName)
        return self.nodes[ind]
        
