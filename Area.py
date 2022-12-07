import numpy as np

class Area:
    def __init__(self, areaName: str, simulationYear: int, climateYear: int):
        self.name = areaName

        self.simulationYear = simulationYear
        self.climateYear = climateYear

        #initialize arrays to hold timeseries
        self.demandTimeSeries = np.zeros(24*365)
        self.PVTimeSeries = np.zeros(24*365)
        self.WSTimeSeries = np.zeros(24*365)
        self.WLTimeSeries = np.zeros(24*365)
        self.CSPTimeSeries = np.zeros(24*365)
        self.HYTimeSeries = np.zeros(24*365) #there should be some relation between this and HyLimit, but i'm not sure i understand. 
        self.OtherResTimeSeries = np.zeros(24*365)
        self.OtherNonResTimeSeries = np.zeros(24*365)

        self.timeSeriesList = [self.demandTimeSeries, self.PVTimeSeries, 
            self.WLTimeSeries, self.WSTimeSeries, self.CSPTimeSeries, 
            self.HYTimeSeries, self.OtherResTimeSeries, self.OtherResTimeSeries] #order of this list must be same as the one returned by CreateProdNamesList

        self.InitializeTimeSeries()

        #variables in timeSeries are normalized, need normalizationfactors from SisyfosData, including the non timedependent production (nonTDProd)
        self.nonTDProd = 0
        self.Demand = 0
        self.PVprod = 0
        self.WSprod = 0
        self.WLprod = 0
        self.CSPprod = 0
        self.HYprod = 0
        self.OtherResProd = 0
        self.OtherNonResProd = 0

        self.InitializeFactors()

    

    def InitializeFactors(self):
        pass


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

    def InitializeTimeSeries(self):
        f = open("data\TVAR.csv","r")
        line = f.readline() #header

        splittedHeader = line.split(";")

        prodNamesList = self.CreateProdNamesList()
        indexArray = np.zeros(len(prodNamesList))-1

        for i in range(len(splittedHeader)):
            for j in range(len(prodNamesList)):
                if(splittedHeader[i] == prodNamesList[j]):
                    indexArray[j] = i
        
        #for i in range(len(indexArray)):
        #    if(indexArray[i] == -1):
        #        print("Warning: did not find " + prodNamesList[i] )

        #now read rest of TVAR, loading the data
        for i in range(24*365):
            line = f.readline()
            line = line.replace(",",".")
            splitted = line.split(";")
            for j in range(len(indexArray)):
                if(indexArray[j] == -1): continue
                self.timeSeriesList[j][i] = splitted[int(indexArray[j])]




    def PrepareHour(self, hour: int):
        pass
    


    def GetName(self):
        return self.name



    #must be able to return the production for a given type for a given hour
    def GetProduction(self, hour: int, type: str):
        return 0



    def GetDemand(self, hour: int):
        return 0