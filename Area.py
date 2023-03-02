import numpy as np
from Production import Production
from DataHolder import DataHolder
from tempfile import mkstemp
from shutil import move, copymode
from os import fdopen, remove
from NonTDProduction import NonTDProduction
from Options import Options

class Area:
    def __init__(self, options: Options, dh: DataHolder, areaName: str, nodeIndex: int, simulationYear: int, climateYear: int):
        self.name = areaName
        self.nodeIndex = nodeIndex
        self.dh = dh
        self.options = options
        print("Preparing area " + self.name)

        self.simulationYear = simulationYear
        self.climateYear = climateYear
        
        #initialize arrays to hold timeseries
        self.demandTimeSeries = dh.GetDemandTimeSeries(nodeIndex)

        #variables in timeSeries are normalized, need normalizationfactors from SisyfosData, including the non timedependent production (nonTDProd)
        self.nonTDProd = NonTDProduction(self.options, "nonTDProd"+self.name)
        self.PVprod = Production(self.options,"PVProd"+self.name)
        self.WSprod = Production(self.options,"WSProd"+self.name)
        self.WLprod = Production(self.options,"WLProd"+self.name)
        self.CSPprod = Production(self.options,"CSPProd"+self.name)
        self.HYprod = Production(self.options,"HYProd"+self.name)
        self.HYlimitprod = Production(self.options,"HYlimitProd"+self.name)
        self.OtherResProd = Production(self.options,"OtherResProd"+self.name)
        self.OtherNonResProd = Production(self.options,"OtherNonResProd"+self.name)
        self.ICHP = Production(self.options,"ICHPProd"+self.name)
        self.demand = Production(self.options,"nonTDProd"+self.name)

        self.productionList = [self.PVprod,self.WSprod,self.WLprod,self.CSPprod,self.HYprod,self.HYlimitprod,self.OtherResProd,self.OtherNonResProd,self.ICHP,self.nonTDProd]

        #list of timeSeries in same order as productionList.
        self.timeSeriesProductionList = dh.GetProdTimeSeriesArray(nodeIndex)

        self.nonTDProdTimeseries = np.zeros(8760)
        
        self.InitializeFactors()
        self.InitializeDemand()

        self.LoadOrCreateOutagePlan()


    def CreateOutagePlan(self):
        print("Creating outage plan for " + self.name)
        #When creating an outage plan, we're creating a pseudo time series for the non-time dependent productions. So what i want is to
        #create an array with the dimensions of number of plants * number of hours.
        noPlants = self.nonTDProd.GetNumberOfPlants()

        capacities = self.nonTDProd.GetCapacityArray()
        noUnits = self.nonTDProd.GetNoUnitsArray()
        plantNames = self.nonTDProd.GetNamesList()
        plannedOutages = self.nonTDProd.GetPlannedOutageArray()

        unitCapacity = capacities/noUnits

        #the matrix that i'm creating should countain how many units of each plant is on in each hour.
        onMatrix = np.zeros([noPlants, 8760])
        for i in range(8760):
            for j in range(noPlants):
                onMatrix[j][i] = noUnits[j]

        demandCopy = self.demand.GetCurrentValue() * self.demandTimeSeries

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

        #we can now create a time series for the nonTDProd
        unitCapacity = capacities/noUnits
        for i in range(8760):
            for j in range(noPlants):
                self.nonTDProdTimeseries[i] += onMatrix[j][i] * unitCapacity[j]

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
        return onMatrix


    def LoadOrCreateOutagePlan(self):
        if(not self.dh.outagePlanLoaded):
            print("Outage plan not loaded")
            self.nonTDProd.SetOutagePlan(self.CreateOutagePlan())
        else:
            self.nonTDProd.SetOutagePlan(self.dh.GetOutagePlan(self.name))



    def InitializeFactors(self):
        factories = self.dh.productionDict[self.name]
        for i in range(len(factories)):
            name = factories[i].name
            cap = float(factories[i].capacity)
            noUnits = 1
            type = factories[i].type
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
                self.nonTDProd.AddProducer(name, cap, noUnits, unplanned, planned, outageTime, heatDep, type)
            else: 
                typeArea = factories[i].variation.split("_")
                if(len(typeArea) == 1):
                    prodType = typeArea[0]
                    prodIndex = self.dh.productionTypes.index(prodType, 0, len(self.dh.productionTypes))
                    self.productionList[prodIndex].AddProducer(name, cap, noUnits, unplanned, planned, outageTime, heatDep, type)
                else: 
                    prodType = typeArea[0].rstrip().lower()
                    area = typeArea[1].rstrip().lower()
                    prodIndex = self.dh.GetProductionIndex(prodType)
                    areaIndex = self.dh.GetAreaIndex(area)
                    if(not areaIndex == self.nodeIndex):
                        #the timeseries for this node is the same is the timeseries for a different node; update.
                        self.timeSeriesProductionList[prodIndex] = self.dh.prodTimeSeriesArray[areaIndex][prodIndex]
                        print("For production of " + prodType + " in " + self.name + " using time series from " + area)
                    prodType = typeArea[0].rstrip()
                    prodIndex = self.dh.productionTypes.index(prodType, 0, len(self.dh.productionTypes))
                    self.productionList[prodIndex].AddProducer(name, cap, noUnits, unplanned, planned, outageTime, heatDep, type)
                    
        self.nonTDProd.SetHeatBinding(self.dh.GetTemperatureArray())

        for prod in self.productionList:
            prod.CreateArrays()




    def PrepareHour(self, hour: int):
        self.nonTDProd.PrepareHour(hour)
    


    def GetName(self):
        return self.name



    #must be able to return the production for a given type for a given hour
    def GetProduction(self, hour: int, typeIndex: int):
        if(typeIndex == (len(self.timeSeriesProductionList)-1)):
            return self.nonTDProd.currentValue
        else:
            return self.timeSeriesProductionList[typeIndex][hour]*self.productionList[typeIndex].GetCurrentValue()


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
        f = open("data/relativeDemands.txt","r")
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

        self.demand.AddProducer("demand" + self.name, demand, 1, 0, 0, 0, 0, "demand")

        self.demand.CreateArrays()

    def GetDemand(self, hour: int, currentAreaIndex: int):
        #demand in TVAR is given in units such that it sums to 1TWh over a year. So it is units of MWh. 
        #the factor is TWh. Means if we just multiply the timeSeries number with the factor, we get the
        #right total demand.
        Final_demand = self.demand.GetCurrentValue() * self.demandTimeSeries[hour]
        return Final_demand