import numpy as np
from Production import Production
from DataHolder import DataHolder
from tempfile import mkstemp
from shutil import move, copymode
from os import fdopen, remove
import random

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
        self.nonTDProd = Production("nonTDProd"+self.name)
        self.PVprod = Production("PVProd"+self.name)
        self.WSprod = Production("WSProd"+self.name)
        self.WLprod = Production("WLProd"+self.name)
        self.CSPprod = Production("CSPProd"+self.name)
        self.HYprod = Production("HYProd"+self.name)
        self.HYlimitprod = Production("HYlimitProd"+self.name)
        self.OtherResProd = Production("OtherResProd"+self.name)
        self.OtherNonResProd = Production("OtherNonResProd"+self.name)
        self.ICHP = Production("ICHPProd"+self.name)
        self.demand = Production("nonTDProd"+self.name)

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


    def LoadOrCreateOutagePlan(self):
        if(not self.dh.outagePlanLoaded):
            print("Outage plan not loaded")
            self.CreateOutagePlan()
        else: 
            capacities = self.nonTDProd.GetCapacityArray()
            noUnits = self.nonTDProd.GetNoUnitsArray()
            noPlants = self.nonTDProd.GetNumberOfPlants()
            unitCapacity = capacities/noUnits
            outagePlan = self.dh.GetOutagePlan(self.name)

            #also simulate spontaneous failure of plants. 
            failedUnits = np.zeros(noPlants)
            unplannedOutage = self.nonTDProd.GetUnplannedOutageArray()
            outageDuration = self.nonTDProd.GetOutageTimeArray()

            for i in range(8760):
                for j in range(noPlants):
                    if(unplannedOutage[j] == 0 or outageDuration[j] == 0):
                        self.nonTDProdTimeseries[i] += (outagePlan[j][i] - failedUnits[j]) * unitCapacity[j]
                    else:
                        #allow units to fail
                        #the odds of going from working to failed (given on page 6 in baggrundsrapport) is
                        failureOdds = unplannedOutage[j]/(outageDuration[j]*(1-unplannedOutage[j]))
                        newFails = 0
                        for k in range(int(noUnits[j]) - int(failedUnits[j])):
                            #generate number between 0 and 1 - if below failure odds, unit fails. 
                            rand = random.random()
                            if(rand < failureOdds):
                                newFails += 1
                        failedUnits[j] += newFails

                        self.nonTDProdTimeseries[i] += (outagePlan[j][i] - failedUnits[j]) * unitCapacity[j]

                        #now allow failed units to regenerate. The odds are
                        regenOdds = 1 / unplannedOutage[j]
                        newRegens = 0
                        for k in range(int(failedUnits[j])):
                            rand = random.random()
                            if(rand < regenOdds):
                                newRegens += 1
                        failedUnits[j] -= newRegens




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
                self.nonTDProd.AddProducer(splitted[0], float(splitted[3]), int(splitted[4]) , float(splitted[6]), float(splitted[7]), int(splitted[8]), float(splitted[10]) )
            else:
                typeArea = splitted[9].split("_")
                if(len(typeArea) == 1):
                    type = typeArea[0]
                    prodIndex = self.dh.productionTypes.index(type, 0, len(self.dh.productionTypes))
                    self.productionList[prodIndex].AddProducer(splitted[0], float(splitted[3]), int(splitted[4]) , float(splitted[6]), float(splitted[7]), int(splitted[8]), float(splitted[10]) )
                else:
                    type = typeArea[0].rstrip().lower()
                    area = typeArea[1].rstrip().lower()
                    prodIndex = self.dh.GetProductionIndex(type)
                    areaIndex = self.dh.GetAreaIndex(area)
                    if(not areaIndex == self.nodeIndex):
                        #the timeseries for this node is the same is the timeseries for a different node; update.
                        self.timeSeriesProductionList[prodIndex] = self.dh.prodTimeSeriesArray[areaIndex][prodIndex]
                        print("For production of " + type + " in " + self.name + " using time series from " + area)
                    self.productionList[prodIndex].AddProducer(splitted[0], float(splitted[3]), int(splitted[4]) , float(splitted[6]), float(splitted[7]), int(splitted[8]), float(splitted[10]) )
            line = f.readline()

        for prod in self.productionList:
            prod.CreateArrays()




    def PrepareHour(self, hour: int):
        pass
    


    def GetName(self):
        return self.name



    #must be able to return the production for a given type for a given hour
    def GetProduction(self, hour: int, typeIndex: int):
        if(typeIndex == (len(self.timeSeriesProductionList)-1)):
            return self.nonTDProdTimeseries[hour]
        else:
            return self.timeSeriesProductionList[typeIndex][hour]*self.productionList[typeIndex].GetCurrentValue()


    def InitializeDemand(self):
        f = open("data/areadata"+str(self.simulationYear)+".csv","r") 
        demand = f.readline() #skip header
        demand = f.readline() #reads first line
        while(demand):
            splitted = demand.split(",")
            if(splitted[0].__eq__(self.name)):
                self.demand.AddProducer("demand" + self.name, float(splitted[1]), 1, 0, 0, 0, 0)
            demand = f.readline()
        
        self.demand.CreateArrays()

    def GetDemand(self, hour: int, currentAreaIndex: int):
        #demand in TVAR is given in units such that it sums to 1TWh over a year. So it is units of MWh. 
        #the factor is TWh. Means if we just multiply the timeSeries number with the factor, we get the
        #right total demand.
        Final_demand = self.demand.GetCurrentValue() * self.demandTimeSeries[hour]
        return Final_demand