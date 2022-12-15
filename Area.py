import numpy as np
import DataHolder as DataHolder

class Area:
    def __init__(self, areaName: str, nodeIndex: int, simulationYear: int, climateYear: int, dh: DataHolder, productionList):
        self.name = areaName
        self.nodeIndex = nodeIndex
        print("Preparing area " + self.name)

        self.simulationYear = simulationYear
        self.climateYear = climateYear
        
        self.demandValues = np.zeros(26)
        self.productionList = productionList
        
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
        self.OtherResProd = wrap(0)
        self.OtherNonResProd = wrap(0)

        #list of timeSeries in same order as productionList.
        self.timeSeriesProductionList = dh.GetProdTimeSeriesArray(nodeIndex)

        self.InitializeFactors()

    

    def InitializeFactors(self):
        f = open("data\plantdata"+str(self.simulationYear)+".csv", "r")
        #iterate over lines to get plant data
        line = f.readline()
        while(line):
            splitted = line.split(",")
            if(splitted[1] == self.name):
                if("PV" in splitted[0]):
                    self.PVprod.v += float(splitted[3])
                elif("WindSea" in splitted[0]):
                    self.WSprod.v += float(splitted[3])
                elif("WindLand" in splitted[0]):
                    self.WSprod.v += float(splitted[3])
                elif("SolarTh" in splitted[0]):
                    self.CSPprod.v += float(splitted[3])
                elif("Hydro" in splitted[0]):
                    self.HYprod.v += float(splitted[3])
                elif("OtherRES" in splitted[0]):
                    self.OtherResProd.v += float(splitted[3])
                elif("OtherNonRES" in splitted[0]):
                    self.OtherNonResProd.v += float(splitted[3])
                else:
                    self.nonTDProd.v += float(splitted[3])
            line = f.readline()

    def CreateProdNamesList(self):
        demandYear = str(self.simulationYear)[2:]
        if(self.simulationYear == 2040):
            demandYear = "30"

        #first get indeces to read in TVAR
        demandName = "DNT" + demandYear + "_" + str(self.climateYear) + "_" + self.name
        PVName = "PV" + str(self.climateYear)+"_30_" + self.name
        WLName = "WL" + str(self.climateYear)+"_" + str(self.simulationYear)[2:] + "_" + self.name
        WSName = "WS" + str(self.climateYear)+"_" + str(self.simulationYear)[2:] + "_" + self.name
        CSPName = "CSP" + str(self.climateYear)+"_30_" + self.name
        HYName = "HY" + str(self.climateYear)+"_" + self.name
        OtherRESName = "OtherRES_" + self.name
        OtherNonRESName = "OtherNonRES_" + self.name

        return [demandName,PVName,WLName,WSName,CSPName,HYName,OtherRESName,OtherNonRESName]



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



    def GetDemand(self, hour: int, currentAreaIndex: int):
        f = open("data\\areadata"+str(self.simulationYear)+".csv","r") 
        demand = f.readline() #skip header
        demand = f.readline() #reads first line
        for j in range(len(self.demandValues)):
            splitted = demand.split(",")
            demand_value = float(splitted[1])
            self.demandValues[j] = demand_value
            demand = f.readline()
        Final_demand = self.demandValues[currentAreaIndex] * self.demandTimeSeries[hour]
        return Final_demand

#need pass by reference for ints; wrapper class needed. 
class wrap:
    def __init__(self, value):
         self.v = value