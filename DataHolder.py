import numpy as np

#class for holding global data for use in the other classes 
#also reads TVAR.csv only once, so it does not need to be read by all areas as timeseries are initialized.
class DataHolder:
    def __init__(self, simulationYear: int, climateYear: int):
        self.names = ["DK1", "DK2", "DKBO", "DKKF", "DKEI", "NOn","NOm","NOs","SE1","SE2","SE3","SE4","FI","DELU","AT","NL","GB","FR","BE","ESPT","CH","IT","EELVLT", "PL", "CZSK","HU"]
        self.simpleNames = []
        self.productionTypes = ["PV","WS","WL","CSP","HY","HYlimit","OtherRes","OtherNonRes","ICHP","nonTDProd"]
        self.simpleProductionTypes = []

        for name in self.names:
            self.simpleNames.append(name.lower())

        for prod in self.productionTypes:
            self.simpleProductionTypes.append(prod.lower())

        self.simpleNames = []
        self.productionTypes = ["PV","WS","WL","CSP","HY","HYlimit","OtherRes","OtherNonRes","ICHP","nonTDProd"]
        self.simpleProductionTypes = []

        for name in self.names:
            self.simpleNames.append(name.lower())

        for prod in self.productionTypes:
            self.simpleProductionTypes.append(prod.lower())

        self.simulationYear = simulationYear
        self.climateYear = climateYear

        self.prodTimeSeriesArray = []
        self.demandTimeSeries = []

        self.InitializeEmptyTimeSeriesArray()
        self.InitializeTimeSeries()

    def CreateProdNamesList(self, name):
        demandYear = str(self.simulationYear)[2:]
        if(self.simulationYear == 2040):
            demandYear = "30"

        #first get indeces to read in TVAR
        demandName = "DNT" + demandYear + "_" + str(self.climateYear) + "_" + name
        PVName = "PV" + str(self.climateYear)+"_30_" + name
        WLName = "WL" + str(self.climateYear)+"_" + str(self.simulationYear)[2:] + "_" + name
        WSName = "WS" + str(self.climateYear)+"_" + str(self.simulationYear)[2:] + "_" + name
        CSPName = "CSP" + str(self.climateYear)+"_30_" + name
        HYName = "HY" + str(self.climateYear)+"_" + name
        HylimitName = "Hylimit" + "_" + name
        OtherRESName = "OtherRes_" + name
        OtherNonRESName = "OtherNonRes_" + name

        if(name == "DKBO"):
            demandName = "DNT" + demandYear + "_" + str(self.climateYear) + "_" + "DK2"

        if(name == "DKKF"):
            demandName = "DNT" + demandYear + "_" + str(self.climateYear) + "_" + "DK2"

        if(name == "DKEI"):
            demandName = "DNT" + demandYear + "_" + str(self.climateYear) + "_" + "DK1"

        return [demandName,PVName,WSName,WLName,CSPName,HYName,HylimitName,OtherRESName,OtherNonRESName,"ICHP"]

    def InitializeEmptyTimeSeriesArray(self):
        for i in range(len(self.names)):
            self.demandTimeSeries.append(np.zeros(24*365))

            build = []
            for j in range(len(self.productionTypes)-1):
                build.append(np.zeros(24*365))

            build.append(1) #for nonTDprod
            self.prodTimeSeriesArray.append(build)

    def InitializeTimeSeries(self):
        f = open("data/TVAR.csv","r")
        line = f.readline() #header

        line.rstrip('\r')
        splittedHeader = line.split(";")

        indexArray = []
        prodNameArray = []
        
        for i in range(len(self.names)):
            prodNamesList = self.CreateProdNamesList(self.names[i])

            for j in range(len(prodNamesList)):
                prodNamesList[j] = prodNamesList[j].lower()


            for j in range(len(prodNamesList)):
                prodNamesList[j] = prodNamesList[j].lower()

            areaIndexArray = np.zeros(len(prodNamesList))-1

            for k in range(len(splittedHeader)):
                splittedHeader[k] = splittedHeader[k].rstrip().lower()
                splittedHeader[k] = splittedHeader[k].rstrip().lower()
                for j in range(len(prodNamesList)):
                    if(splittedHeader[k].__eq__(prodNamesList[j])):
                        areaIndexArray[j] = k


            #found the indeces for this area.
            indexArray.append(areaIndexArray)
            prodNameArray.append(prodNamesList)




        for i in range(len(indexArray)):
            for j in range(len(indexArray[i])):
                if(indexArray[i][j] == -1):
                    print("Warning: did not find " + prodNameArray[i][j] )
            
        print("Reading TVAR.csv")
        #now read rest of TVAR, loading the data
        for i in range(24*365):
            line = f.readline()
            line.rstrip('\r')
            line.rstrip('\r')
            line = line.replace(",",".")
            splitted = line.split(";")
            for j in range(len(indexArray)):
                for k in range(len(indexArray[j])):
                    if(indexArray[j][k] == -1): continue
                    if(k == 0):
                        self.demandTimeSeries[j][i] = splitted[int(indexArray[j][k])]
                    else:
                        self.prodTimeSeriesArray[j][k-1][i] = splitted[int(indexArray[j][k])]

    def GetProdTimeSeriesArray(self, nodeIndex: int):
        return self.prodTimeSeriesArray[nodeIndex]
    
    def GetDemandTimeSeries(self, nodeIndex: int):
        return self.demandTimeSeries[nodeIndex]

    def GetAreaIndex(self, name: str):
        return self.simpleNames.index(name, 0, len(self.simpleNames))
        
    def GetProductionIndex(self, prod: str):
        return self.simpleProductionTypes.index(prod, 0, len(self.simpleProductionTypes))

    def GetAreaIndex(self, name: str):
        return self.simpleNames.index(name, 0, len(self.simpleNames))
        
    def GetProductionIndex(self, prod: str):
        return self.simpleProductionTypes.index(prod, 0, len(self.simpleProductionTypes))