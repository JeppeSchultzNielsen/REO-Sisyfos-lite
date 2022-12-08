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

        #put productions in list like in DataHolder
        self.productionList = [self.PVprod,self.WSprod,self.WLprod,self.CSPprod,self.HYprod,self.OtherResProd,self.OtherNonResProd,self.nonTDProd]

        #list of timeSeries in same order as productionList.
        self.timeSeriesProductionList = [self.PVTimeSeries, self.WSTimeSeries,self.WLTimeSeries, self.CSPTimeSeries,
            self.HYTimeSeries, self.OtherResProd, self.OtherNonResProd]

        self.InitializeFactors()

        if(self.name == "DK1"):
            print(self.PVprod)

    

    def InitializeFactors(self):
        f = open("data\plantdata"+str(self.simulationYear)+".csv", "r")
        #iterate over lines to get plant data
        line = f.readline()
        while(line):
            splitted = line.split(",")
            if(splitted[1] == self.name):
                if("PV" in splitted[0]):
                    self.PVprod += float(splitted[3])
                elif("WindSea" in splitted[0]):
                    self.WSprod += float(splitted[3])
                elif("WindLand" in splitted[0]):
                    self.WSprod += float(splitted[3])
                elif("SolarTh" in splitted[0]):
                    self.CSPprod += float(splitted[3])
                elif("Hydro" in splitted[0]):
                    self.HYprod += float(splitted[3])
                elif("OtherRES" in splitted[0]):
                    self.OtherResProd += float(splitted[3])
                elif("OtherNonRES" in splitted[0]):
                    self.OtherNonResProd += float(splitted[3])
                else:
                    self.nonTDProd += float(splitted[3])
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
    def GetProduction(self, hour: int, typeIndex: int):
        if(typeIndex == len(self.timeSeriesProductionList)):
            return self.nonTDProd
        else:
            return self.timeSeriesProductionList[typeIndex][hour]*self.productionList[typeIndex]



    def GetDemand(self, hour: int):
        return 0