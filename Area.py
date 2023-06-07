import numpy as np
from Production import Production
from DataHolder import DataHolder
from tempfile import mkstemp
from shutil import move, copymode
from os import fdopen, remove
from NonTDProduction import NonTDProduction
from Options import Options

class Area:
    def __init__(self, options: Options, dh: DataHolder, areaName: str, nodeIndex: int):
        self.name = areaName
        self.nodeIndex = nodeIndex
        self.dh = dh
        self.options = options
        print("Preparing area " + self.name)

        self.simulationYear = options.simulationYear
        self.climateYear = options.climateYear
        
        #initialize arrays to hold timeseries
        self.demandTimeSeries = dh.GetDemandTimeSeries(nodeIndex)

        #variables in timeSeries are normalized, need normalizationfactors from SisyfosData, including the non timedependent production (nonTDProd)
        self.demand = Production(self.options,"demand"+self.name)
        self.nonTDdemand = NonTDProduction(self.options,"RS_flat_"+self.name)

        self.productionList = []
        self.productionNames = []
        self.nonTDProductionList = []
        self.nonTDProductionNames = []
        self.variableProd = []

        #list of timeSeries in same order as productionList.
        self.timeSeriesProductionList = dh.GetProdTimeSeriesArray(nodeIndex)

        self.InitializeDemand()
        self.InitializeFactors()

        self.LoadOrCreateOutagePlan()

        self.totProductionList = self.productionList+self.nonTDProductionList
        self.totProductionNames = self.productionNames+self.nonTDProductionNames

    def GetDiagString(self):
        build = "Name\tType\tCapacity\tNoUnits\tPlannedOutage\tUnplannedOutage\tOutageTime\tHeatDep\tVariation\n"
        printList = self.totProductionList.copy()
        printList.append(self.demand)
        printList.append(self.nonTDdemand)
        for i in range(len(printList)):
            for j in range(len(printList[i].nameList)):
                build += printList[i].nameList[j] + "\t"
                build += printList[i].name + "\t"
                build += str(printList[i].capacityArray[j]) + "\t"
                build += str(printList[i].noUnitsArray[j]) + "\t"
                build += str(printList[i].plannedOutageArray[j]) + "\t"
                build += str(printList[i].unplannedOutageArray[j]) + "\t"
                build += str(printList[i].outageTimeArray[j]) + "\t"
                build += str(printList[i].heatDependenceArray[j]) + "\t"
                build += str(printList[i].variationList[j]) + "\n"

        return build


    def CreateOutagePlan(self):
        print("Creating outage plan for " + self.name)
        noPlants = 0
        onMatrix = np.zeros([noPlants, 8760])
        plantNames = np.array([])

        if(len(self.nonTDProductionList) > 0):
            noPlants = self.nonTDProductionList[0].GetNumberOfPlants()
            capacities = self.nonTDProductionList[0].GetCapacityArray()
            noUnits = self.nonTDProductionList[0].GetNoUnitsArray()
            plantNames = self.nonTDProductionList[0].GetNamesList()
            plannedOutages = self.nonTDProductionList[0].GetPlannedOutageArray()

            for i in range(len(self.nonTDProductionList)-1):
                i = i+1
                noPlants = noPlants + self.nonTDProductionList[i].GetNumberOfPlants()
                capacities = np.concatenate([capacities,self.nonTDProductionList[i].GetCapacityArray()])
                noUnits = np.concatenate([noUnits,self.nonTDProductionList[i].GetNoUnitsArray()])
                plantNames = np.concatenate([plantNames,self.nonTDProductionList[i].GetNamesList()])
                plannedOutages = np.concatenate([plannedOutages,self.nonTDProductionList[i].GetPlannedOutageArray()])

            unitCapacity = capacities/noUnits

            #the matrix that i'm creating should countain how many units of each plant is on in each hour.
            onMatrix = np.zeros([noPlants, 8760])
            for i in range(8760):
                for j in range(noPlants):
                    onMatrix[j][i] = noUnits[j]

            demandCopy = np.zeros(8760)
            for i in range(8760):
                demandCopy[i] += self.demand.GetCurrentValue(i)

            if(self.options.useVariations):
                for i in range(len(self.productionList)-1):
                    for j in range(8760):
                        demandCopy[j] -= self.productionList[i].GetCurrentValue(j)

            #now i will iterate over all units. 
            for i in range(noPlants):
                #first place the units with highest capacities.
                indexMax = int(np.argmax(unitCapacity))

                outageHours = int(plannedOutages[indexMax]*8760 + 0.5)
                for j in range(noUnits[indexMax]):
                    #now find the hours in demandCopy where this does least damage; this is where the sum over 
                    #the outage hours is smallest (least demand)
                    smallestIndex = 0
                    smallest = 10e9
                    for k in range(8760 - outageHours):
                        currentSum = sum( demandCopy[k:k+outageHours] )
                        if( currentSum < smallest ):
                            smallest = currentSum
                            smallestIndex = k
                    
                    #adjust the on-matrix accordingly. 
                    for k in range(outageHours):
                            onMatrix[indexMax][smallestIndex+k] -= 1
                            #adjust the demandCopy accordingly - surplus demand falls because a unit is off now - equivalent to demand rising. 
                            demandCopy[smallestIndex+k] += unitCapacity[indexMax]
                #having solved the problem for this unitCapacity, we can set it to zero and do it over again with next highest unit capacity. 
                unitCapacity[indexMax] = -10e9

        #save this outage plan for future use. 
        outagePlanPath = self.dh.GetOutagePlanPath()
        #create temporary file to write to. 2nd answer in https://stackoverflow.com/questions/39086/search-and-replace-a-line-in-a-file-in-python
        fh, abs_path = mkstemp()

        i = 0
        with fdopen(fh,'w') as new_file:
            with open(outagePlanPath) as old_file:
                for line in old_file:
                    if(i == 0):
                        #line is header. Add header so far with additions:
                        newLine = line.rstrip() + "\t" + self.name
                        for j in range(noPlants):  
                            newLine += "\t" + plantNames[j]
                        new_file.write(newLine )
                    else:
                        newLine = "\r" + line.rstrip() + "\t-"
                        for j in range(noPlants): 
                            newLine += "\t" + str(onMatrix[j][i-1])
                        new_file.write(newLine )
                    i += 1

        copymode(outagePlanPath, abs_path)
        #Remove original file
        remove(outagePlanPath)
        #Move new file
        move(abs_path, outagePlanPath)
        return (plantNames, onMatrix)


    def LoadOrCreateOutagePlan(self):
        if(not self.dh.outagePlanLoaded):
            print("Outage plan not loaded")
            (header, outagePlan) = self.CreateOutagePlan()
            for i in range(len(self.nonTDProductionList)):
                self.nonTDProductionList[i].SetOutagePlan(outagePlan,header.tolist())
        else:
            for i in range(len(self.nonTDProductionList)):
                self.nonTDProductionList[i].SetOutagePlan(self.dh.GetOutagePlan(self.name),self.dh.GetOutagePlanHeader(self.name))



    def InitializeFactors(self):
        factories = self.dh.productionDict[self.name]
        for i in range(len(factories)):
            name = factories[i].name
            cap = float(factories[i].capacity)

            if(not self.options.energyIslandWest):
                if(name == "EnergioeVest"):
                    cap = 0
            if(not self.options.energyIslandEast):
                if(name == "EnergioeEast"):
                    cap = 0
                    
            noUnits = 1
            type = factories[i].type
            if(cap == 0):
                continue
            if(type == "DSR" and not self.options.useDSR):
                continue
            if(factories[i].noUnits == "-"):
                if(self.dh.outageDict[type].unitSize < 0.0000001):
                    noUnits = 1 #avoid division by zero
                else:
                    noUnits = max(1 , int(cap/self.dh.outageDict[type].unitSize) )
            else:
                noUnits = int(factories[i].noUnits)
            unplanned = self.dh.outageDict[type].unplanned
            planned = self.dh.outageDict[type].planned
            outageTime = self.dh.outageDict[type].outageTime
            heatDep = self.dh.outageDict[type].heatDep

            if(factories[i].variation == "-" or factories[i].variation == "No_RoR"):
                if(not self.name+"_"+type in self.nonTDProductionNames):
                        if(type == "RS"):
                            #is demand type.
                            pass
                        else:
                        #create new productiontype with this name.
                            self.nonTDProductionList.append(NonTDProduction(self.options,self.name+"_"+type))
                            self.nonTDProductionList[-1].SetHeatBinding(self.dh.GetTemperatureArray())
                            self.nonTDProductionNames.append(self.name+"_"+type)
                            if(self.options.prioritizeNuclear):
                                if(type in ("Nuclear","NuclearSweden","NuclearFinland","Kernekraft_DE","Borssele","NuclearGB","NuclearFR","NuclearBE","NuclearES","NuclearCH","NuclearCZSK","NuclearHU") or "nuclear" in type or "Nuclear" in type):
                                    self.variableProd.append(self.nonTDProductionList[-1])
                if(type == "RS"):
                    if(self.options.useReserve):
                        self.nonTDdemand.AddProducer(name, -cap, noUnits, unplanned, planned, outageTime, heatDep, type,factories[i].variation,self.dh.constantTimeSeries)
                else:
                    prodListIndex = self.nonTDProductionNames.index(self.name+"_"+type,0,len(self.nonTDProductionNames))
                    self.nonTDProductionList[prodListIndex].AddProducer(name, cap, noUnits, unplanned, planned, outageTime, heatDep, type,factories[i].variation,self.dh.constantTimeSeries)
            else: 
                typeArea = factories[i].variation.split("_")
                if(len(typeArea) == 1):
                    #this is ICHP, all others have len 2 when splitted 
                    prodType = typeArea[0]
                    varIndex = self.dh.productionTypes.index(prodType, 0, len(self.dh.productionTypes))
                    if(not self.name+"_"+type in self.productionNames):
                        #create new productiontype with this name.
                        self.productionList.append(Production(self.options,self.name+"_"+type))
                        self.productionNames.append(self.name+"_"+type)
                        #append this same production to variableProd.
                        self.variableProd.append(self.productionList[-1])
                    prodListIndex = self.productionNames.index(self.name+"_"+type,0,len(self.productionNames))
                    self.productionList[prodListIndex].AddProducer(name, cap, noUnits, unplanned, planned, outageTime, heatDep, type,factories[i].variation, self.timeSeriesProductionList[varIndex])
                else:  
                    prodType = typeArea[0].rstrip().lower()
                    area = typeArea[1].rstrip().lower()
                    varIndex = self.dh.GetProductionIndex(prodType)
                    areaIndex = self.dh.GetAreaIndex(area)
                    if(not areaIndex == self.nodeIndex):
                        #the timeseries for this node is the same is the timeseries for a different node; update.
                        print("For production of " + name + " in " + self.name + " using time series from " + area)
                    if(not self.name+"_"+type in self.productionNames):
                        #create new productiontype with this name.
                        self.productionList.append(Production(self.options,self.name+"_"+type))
                        self.productionNames.append(self.name+"_"+type)
                        if(prodType in ("pv","ws","wl","csp","hy","otherres","othernonres","ichp")):
                            #append this same production to variableProd.
                            self.variableProd.append(self.productionList[-1])
                    prodListIndex = self.productionNames.index(self.name+"_"+type,0,len(self.productionNames))
                    self.productionList[prodListIndex].AddProducer(name, cap, noUnits, unplanned, planned, outageTime, heatDep, type,factories[i].variation, self.dh.prodTimeSeriesArray[areaIndex][varIndex])

        for prod in self.productionList:
            prod.CreateArrays()
        for prod in self.nonTDProductionList:
            prod.CreateArrays()
        self.nonTDdemand.CreateArrays()
        self.nonTDdemand.SetOutagePlan([],[])
        self.nonTDdemand.SetHeatBinding(self.dh.GetTemperatureArray())
        #nonTDdemand is not time dependent in any way - only need to prepare it once.
        self.nonTDdemand.PrepareHour(0)


    def PrepareHour(self, hour: int):
        for prod in self.totProductionList:
            prod.PrepareHour(hour)
    


    def GetName(self):
        return self.name



    #must be able to return the production for a given type for a given hour
    def GetProduction(self, hour: int, typeIndex: int):
        return self.totProductionList[typeIndex].GetCurrentValue(hour)




    def InitializeDemand(self):
        #first find demandfactor for this year. 
        f = open("data/demands.txt","r")
        line = f.readline() #skip header
        line = f.readline() #reads first line
        splitted = line.split()
        #find index of current area
        index = 0
        demandFactor = 0
        for i in range(len(splitted)):
            if(splitted[i] == self.name):
                index = i
        while(line):
            splitted = line.split()
            if(not splitted[0].isnumeric()):
                line = f.readline() #reads first line
                continue
            if(int(splitted[0]) == self.simulationYear):
                demandFactor = float(splitted[index])
            line = f.readline() #reads first line

        #find relativeFactor
        relativeFactor = 0
        f = open("data/relativeDemands"+str(self.dh.demandYear)+".txt","r")
        line = f.readline() #reads first line
        splitted = line.split()
        index = 0
        for i in range(len(splitted)):
            if(splitted[i] == self.name):
                index = i
        while(line):
            splitted = line.split()
            if(not splitted[0].isnumeric()):
                line = f.readline() #reads first line
                continue
            if(int(splitted[0]) == self.climateYear):
                relativeFactor = float(splitted[index])
            line = f.readline() #reads first line

        demand = demandFactor * relativeFactor

        self.demand.AddProducer("demand_" + self.name, demand, 1, 0, 0, 0, 0, "demand", self.name + "demand", self.demandTimeSeries)
        self.demand.CreateArrays()

    def GetDemand(self, hour: int):
        #demand in TVAR is given in units such that it sums to 1TWh over a year. So it is units of MWh. 
        #the factor is TWh. Means if we just multiply the timeSeries number with the factor, we get the
        #right total demand.
        Final_demand = self.demand.GetCurrentValue(hour) + self.nonTDdemand.GetCurrentValue(hour)
        return Final_demand