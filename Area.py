import numpy as np
import DataHolder as DataHolder

class Area:
    def __init__(self, areaName: str, nodeIndex: int, simulationYear: int, climateYear: int, dh: DataHolder):
        self.name = areaName
        self.nodeIndex = nodeIndex
        self.dh = dh
        print("Preparing area " + self.name)

        self.simulationYear = simulationYear
        self.climateYear = climateYear
        
        #initialize arrays to hold timeseries
        self.demandTimeSeries = dh.GetDemandTimeSeries(nodeIndex)

        #variables in timeSeries are normalized, need normalizationfactors from SisyfosData, including the non timedependent production (nonTDProd)
        self.nonTDProd = wrap(0)
        self.Demand = wrap(0)
        self.PVprod = wrap(0)
        self.WSprod = wrap(0)
        self.WLprod = wrap(0)
        self.CSPprod = wrap(0)
        self.HYprod = wrap(0)
        self.HYlimitprod = wrap(0)
        self.OtherResProd = wrap(0)
        self.OtherNonResProd = wrap(0)
        self.ICHP = wrap(0)
        self.demand = wrap(0)

        self.productionList = [self.PVprod,self.WSprod,self.WLprod,self.CSPprod,self.HYprod,self.HYlimitprod,self.OtherResProd,self.OtherNonResProd,self.ICHP,self.nonTDProd]

        #list of timeSeries in same order as productionList.
        self.timeSeriesProductionList = dh.GetProdTimeSeriesArray(nodeIndex)
        
        
        self.InitializeFactors()
        self.InitializeDemand()

    

    def InitializeFactors(self):
        f = open("data/plantdata"+str(self.simulationYear)+".csv", "r",errors='replace')
        line = f.readline()
        while(line):
            splitted = line.split(",")
            if(not splitted[1] == self.name):
                line = f.readline()
                continue
            if(splitted[9] == "-" or splitted[9].rstrip() == "No_RoR"):
                #currently RoR is always 1, which does not seem right. But that is the implementation in sisyfos.
                self.nonTDProd.v += float(splitted[3])
            else:
                typeArea = splitted[9].split("_")
                if(len(typeArea) == 1):
                    type = typeArea[0]
                    prodIndex = self.dh.productionTypes.index(type, 0, len(self.dh.productionTypes))
                    self.productionList[prodIndex].v += float(splitted[3])
                else:
                    type = typeArea[0].rstrip().lower()
                    area = typeArea[1].rstrip().lower()
                    prodIndex = self.dh.GetProductionIndex(type)
                    areaIndex = self.dh.GetAreaIndex(area)
                    if(not areaIndex == self.nodeIndex):
                        #the timeseries for this node is the same is the timeseries for a different node; update.
                        self.timeSeriesProductionList[prodIndex] = self.dh.prodTimeSeriesArray[areaIndex][prodIndex]
                        print("For production of " + type + " in " + self.name + " using time series from " + area)
                    self.productionList[prodIndex].v += float(splitted[3])
            line = f.readline()




    def PrepareHour(self, hour: int):
        pass
    


    def GetName(self):
        return self.name



    #must be able to return the production for a given type for a given hour
    def GetProduction(self, hour: int, typeIndex: int):
        if(typeIndex == (len(self.timeSeriesProductionList)-1)):
            return self.nonTDProd.v 
        else:
            return self.timeSeriesProductionList[typeIndex][hour]*self.productionList[typeIndex].v


    def InitializeDemand(self):
        f = open("data/areadata"+str(self.simulationYear)+".csv","r") 
        demand = f.readline() #skip header
        demand = f.readline() #reads first line
        while(demand):
            splitted = demand.split(",")
            if(splitted[0].__eq__(self.name)):
                self.demand.v = float(splitted[1])
            demand = f.readline()

    def GetDemand(self, hour: int, currentAreaIndex: int):
        #demand in TVAR is given in units such that it sums to 1TWh over a year. So it is units of MWh. 
        #the factor is TWh. Means if we just multiply the timeSeries number with the factor, we get the
        #right total demand.
        Final_demand = self.demand.v * self.demandTimeSeries[hour]
        return Final_demand

#need pass by reference for ints; wrapper class needed. 
class wrap:
    def __init__(self, value):
         self.v = value