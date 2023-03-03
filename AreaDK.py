import numpy as np
from Production import Production
from DataHolder import DataHolder
from tempfile import mkstemp
from shutil import move, copymode
from os import fdopen, remove
from NonTDProduction import NonTDProduction
from Options import Options
from Area import Area

class AreaDK(Area):
    def InitializeDemand(self):
        #Denmark has special demands, need special class with unique functions.
        #do similar calculation as cells C15-35 in demand ark in sisyfos data.
        f = open("data/"+self.name+"Demand.txt","r")
        line = f.readline() #header
        header = line.split()[1:]
        line = f.readline()
        toUse = []
        flexibleShares = []
        while(line):
            splitted = line.split()
            if(splitted[0].isnumeric() and int(splitted[0]) == self.simulationYear):
                toUse = splitted[1:]
            if("Potentielt" in line):
                 flexibleShares = splitted[1:]
            line = f.readline()

        print(self.name)

        nonConstDemand = 0
        flatDemand = 0
        for i in range(4): #first 4 is klassiskDemand
            nonConstDemand += float(toUse[i])
            nonConstDemand -= float(toUse[i]) * float(flexibleShares[i]) * self.options.demFlexKlassisk

        for i in range(3): #next 3 is CVP
            i = i + 4
            nonConstDemand += float(toUse[i])
            nonConstDemand -= float(toUse[i]) * float(flexibleShares[i]) * self.options.demFlexCVP

        #next 2 is ptx and datacentres; these are constant demands.
        flatDemand += float(toUse[7]) #dataCentres
        flatDemand += float(toUse[8])*(1-float(flexibleShares[8]) * self.options.demFlexPtX) #PtX

        for i in range(6): #next 8 is transport
            i = i + 9
            nonConstDemand += float(toUse[i])
            nonConstDemand -= float(toUse[i]) * float(flexibleShares[i]) * self.options.demFlexTransport

        if(self.name == "DK2"):
            #remove DKBO's contribution
            nonConstDemand -= 0.23
            
        self.demand.AddProducer("demand" + self.name, nonConstDemand, 1, 0, 0, 0, 0, "demand")

        self.nonTDProd.AddProducer("flatDemand"+self.name, -1-flatDemand/0.00876, 1, 0, 0, 0, 0, "flatDemand")

        self.demand.CreateArrays()

            
