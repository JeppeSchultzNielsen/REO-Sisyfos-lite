import numpy as np
import os as os

#class for holding global data for use in the other classes 
#also reads TVAR.csv only once, so it does not need to be read by all areas as timeseries are initialized.
class DataHolder:
    def __init__(self, simulationYear: int, climateYear: int, outagePlanPath: str):
        self.names = ["DK1", "DK2", "DKBO", "DKKF", "DKEI", "NOn","NOm","NOs","SE1","SE2","SE3","SE4","FI","DELU","AT","NL","GB","FR","BE","ESPT","CH","IT","EELVLT", "PL", "CZSK","HU"]
        self.simpleNames = []
        self.productionTypes = ["PV","WS","WL","CSP","HY","HYlimit","OtherRes","OtherNonRes","ICHP","nonTDProd"]
        self.simpleProductionTypes = []

        self.outagePlanPath = outagePlanPath

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

        self.outageHeaderList = []
        self.outagePlanMatrix = []

        self.InitializeEmptyTimeSeriesArray()
        self.InitializeTimeSeries()

        self.outagePlanLoaded = False
        self.LoadOutagePlan(outagePlanPath)



    def LoadOutagePlan(self, outagePlanPath: str):
        if( os.path.isfile(outagePlanPath) ):
            print("Reading " + outagePlanPath)
            #read header
            read = open(outagePlanPath, "r+")
            line = read.readline()
            line = line.replace("\n","")
            splitted = line.split("\t")

            startIndeces = []
            stopIndeces = []


            #find start and stop indeces for each area
            for name in self.names:
                startIndex = splitted.index(name)
                startIndeces.append(startIndex)

            startIndeces = np.array(startIndeces)

            #can find stop indeces
            for i in range(len(self.names)):
                startIndex = startIndeces[i]
                startIndecesCopy = np.copy(startIndeces)
                for j in range(len(startIndecesCopy)):
                    if(startIndecesCopy[j] <= startIndex):
                        #all these can be discounted
                        startIndecesCopy[j] = 1e7
                stopIndex = np.min(startIndecesCopy)
                stopIndeces.append(stopIndex)

            #largest stopIndex should be the end of the array
            stopIndeces[stopIndeces.index(max(stopIndeces))] = len(splitted)

            #add 1 to start indeces to discard country names
            startIndeces += 1

            #i can now add the names of the factories to a headerlist. 
            for i in range(len(self.names)):
                headerArray = []
                for j in range(stopIndeces[i] - startIndeces[i]):
                    if(j + startIndeces[i] < len(splitted)):
                        headerArray.append( splitted[j+int(startIndeces[i])] )
                self.outageHeaderList.append(headerArray)

            #and i can construct a matrix storing the outage plans. 
            for i in range(len(self.names)):
                self.outagePlanMatrix.append(np.zeros([len(self.outageHeaderList[i]),8760]))

            #now i can fill the matrix with the remaining lines 
            k=0
            line = read.readline()
            while(line):
                line = line.replace("\n","")
                splitted = line.split("\t")
                for i in range(len(self.names)):
                    for j in range(stopIndeces[i] - startIndeces[i]):
                        if(k > 8700):
                            int(float(splitted[j + int(startIndeces[i])]))
                        self.outagePlanMatrix[i][j][k] = int(float(splitted[j + int(startIndeces[i])]))
                k = k+1
                line = read.readline()

            self.outagePlanLoaded = True
        else: 
            print("Outage plan not found! New outage plans will be created in " + str(outagePlanPath) + ", expect long wait")
            write = open(outagePlanPath, "w+")
            write.write("Names" + "\n")
            for i in range(8760):
                write.write(str(i) + "\n")

    def GetOutagePlanPath(self):
        return self.outagePlanPath

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

    def GetOutagePlan(self, areaName: str):
        if(self.outagePlanLoaded):
            nameIndex = self.names.index(areaName)
            factoryIndex = self.outageHeaderList[nameIndex]
            return self.outagePlanMatrix[nameIndex]
        else:
            return np.array([])