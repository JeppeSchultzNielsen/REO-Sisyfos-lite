import numpy as np
from Production import Production
import random
from Options import Options

class NonTDProduction(Production):
    def __init__(self, options: Options, name: str):
        self.options = options
        self.name = name

        self.maxValue = 0
        self.currentValue = 0
        self.capacityList = []
        self.noUnitsList = []
        self.unplannedOutageList = []
        self.plannedOutageList = []
        self.outageTimeList = []
        self.heatDependenceList = []
        self.nameList = []
        self.typesList = []
        self.variationList = []

        self.capacityArray = 0
        self.unplannedOutageArray = 0
        self.plannedOutageArray = 0
        self.outageTimeArray = 0
        self.heatDependenceArray = 0
        self.noUnitsArray = 0
        self.noFunctioningUnitsArray = 0

        self.outagePlan = 0
        self.failedUnits = 0

        self.currentPlannedOutage = 0
        self.currentUnplannedOutage = 0

        self.outagePlanHeader = 0

        self.failedUnitsInitialized = False

    def SetOutagePlan(self, outagePlan, outagePlanHeader):
        self.outagePlanHeader = outagePlanHeader
        self.outagePlan = np.zeros([len(self.capacityArray),8760])
        for i in range(len(self.capacityArray)):
            if(outagePlanHeader.count(self.nameList[i])):
                ind = outagePlanHeader.index(self.nameList[i])
                self.outagePlan[i] = outagePlan[ind]
            else:
                print("Warning: no outage plan found for " + self.nameList[i] + " defaulting to always on.")
                self.outagePlan[i] = self.outagePlan[i]+self.noUnitsArray[i]
        if(not self.options.usePlannedDownTime):
            #outageMatrix should just be full at all times. 
            for i in range(len(self.capacityArray)):
                for j in range(len(self.outagePlan[i])):
                    outagePlan[i][j] = self.noUnitsArray[i]

    def SetHeatBinding(self, heatBinding):
        self.heatBinding = heatBinding

    def CreateArrays(self):
        super().CreateArrays()
        self.failedUnits = np.zeros(self.GetNumberOfPlants())

    def GetCurrentPlannedOutage(self):
        return self.currentPlannedOutage
    
    def GetCurrentUnplannedOutage(self):
        return self.currentUnplannedOutage
    
    def InitializeFailedUnits(self, startingHour: int):
        #at the start of the simulation, all units should by some probability be failed; assume the odds that they are failed
        #is their %downtime.
        if(self.options.useUnplannedDownTime):
            for i in range(len(self.capacityArray)):
                    newFails = 0
                    for j in range(int(self.outagePlan[i][startingHour])):
                        rand = random.random()
                        if(rand < self.unplannedOutageArray[i]):
                            newFails += 1
                    self.failedUnits[i] = newFails

        self.failedUnitsInitialized = True

    def AddProducer(self, name: str, capacity: float, noUnits: int, unplannedOutage: float, plannedOutage: float, outageTime: int, heatDependence: float, type: str, variation: str):
        self.nameList.append(name)
        self.capacityList.append(capacity)
        self.unplannedOutageList.append(unplannedOutage)
        self.plannedOutageList.append(plannedOutage)
        self.outageTimeList.append(outageTime)
        self.heatDependenceList.append(heatDependence)
        self.noUnitsList.append(noUnits)
        self.typesList.append(type)
        self.variationList.append(variation)


    def PrepareHour(self, hour: int):
        #if this is the first hour, initialize failedUnits
        if(not self.failedUnitsInitialized):
            self.InitializeFailedUnits(hour)

        #iterate over all plants to get the total production in this hour
        self.currentValue = 0; 
        self.currentPlannedOutage = 0
        self.currentUnplannedOutage = 0

        noPlants = len(self.capacityArray)
        for j in range(noPlants):
                if(self.unplannedOutageArray[j] == 0 or self.outageTimeArray[j] == 0):
                    #these plants cannot fail randomly, add them straight with heat binding. 
                    prod = self.outagePlan[j][hour] / self.noUnitsArray[j] * self.capacityArray[j]
                    self.currentValue += prod*(1-self.heatDependenceArray[j]) + self.heatDependenceArray[j]*self.heatBinding[j]*prod
                else:
                    #allow failed units to regenerate. The odds are
                    regenOdds = 1 / self.outageTimeArray[j]
                    newRegens = 0
                    for k in range(int(self.failedUnits[j])):
                        rand = random.random()
                        if(rand < regenOdds):
                            newRegens += 1
                    self.failedUnits[j] -= newRegens

                    #allow units to fail
                    #the odds of going from working to failed (given on page 6 in baggrundsrapport) is
                    failureOdds = self.unplannedOutageArray[j]/(self.outageTimeArray[j]*(1-self.unplannedOutageArray[j]))
                    if(not self.options.useUnplannedDownTime):
                        failureOdds = 0
                    newFails = 0
                    for k in range(int(self.outagePlan[j][hour]) - int(self.failedUnits[j])):
                        #generate number between 0 and 1 - if below failure odds, unit fails. 
                        rand = random.random()
                        if(rand < failureOdds):
                            newFails += 1
                    self.failedUnits[j] += newFails

                    #add production with heatbinding
                    prod = (self.outagePlan[j][hour] - self.failedUnits[j])/ self.noUnitsArray[j] * self.capacityArray[j]
                    self.currentValue += prod*(1-self.heatDependenceArray[j]) + self.heatDependenceArray[j]*self.heatBinding[j]*prod
                    
                    prod = (self.noUnitsArray[j]-self.outagePlan[j][hour])/ self.noUnitsArray[j] * self.capacityArray[j]
                    self.currentPlannedOutage += prod*(1-self.heatDependenceArray[j]) + self.heatDependenceArray[j]*self.heatBinding[j]*prod

                    prod = (self.failedUnits[j])/ self.noUnitsArray[j] * self.capacityArray[j]
                    self.currentUnplannedOutage += prod*(1-self.heatDependenceArray[j]) + self.heatDependenceArray[j]*self.heatBinding[j]*prod