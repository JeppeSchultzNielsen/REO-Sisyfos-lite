import numpy as np
from Production import Production
import random

class NonTDProduction(Production):
    def __init__(self, name: str):
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

        self.capacityArray = 0
        self.unplannedOutageArray = 0
        self.plannedOutageArray = 0
        self.outageTimeArray = 0
        self.heatDependenceArray = 0
        self.noUnitsArray = 0
        self.noFunctioningUnitsArray = 0

        self.outagePlan = 0
        self.failedUnits = 0

    def SetOutagePlan(self, outagePlan):
        self.outagePlan = outagePlan

    def SetHeatBinding(self, heatBinding):
        self.heatBinding = heatBinding

    def CreateArrays(self):
        super().CreateArrays()
        self.failedUnits = np.zeros(self.GetNumberOfPlants())

    def PrepareHour(self, hour: int):
        #iterate over all plants to get the total production in this hour
        self.currentValue = 0; 
        noPlants = len(self.capacityArray)
        for j in range(noPlants):
                if(self.unplannedOutageArray[j] == 0 or self.outageTimeArray[j] == 0):
                    #these plants cannot fail randomly, add them straight with heat binding. 
                    prod = self.outagePlan[j][hour] / self.noUnitsArray[j] * self.capacityArray[j]
                    self.currentValue += prod*(1-self.heatDependenceArray[j]) + self.heatDependenceArray[j]*self.heatBinding[j]*prod
                else:
                    #allow units to fail
                    #the odds of going from working to failed (given on page 6 in baggrundsrapport) is
                    failureOdds = self.unplannedOutageArray[j]/(self.outageTimeArray[j]*(1-self.unplannedOutageArray[j]))
                    newFails = 0
                    for k in range(int(self.noUnitsArray[j]) - int(self.failedUnits[j])):
                        #generate number between 0 and 1 - if below failure odds, unit fails. 
                        rand = random.random()
                        if(rand < failureOdds):
                            newFails += 1
                    self.failedUnits[j] += newFails

                    #add production with heatbinding
                    prod = (self.outagePlan[j][hour] - self.failedUnits[j])/ self.noUnitsArray[j] * self.capacityArray[j]
                    self.currentValue += prod*(1-self.heatDependenceArray[j]) + self.heatDependenceArray[j]*self.heatBinding[j]*prod

                    #now allow failed units to regenerate. The odds are
                    regenOdds = 1 / self.outageTimeArray[j]
                    newRegens = 0
                    for k in range(int(self.failedUnits[j])):
                        rand = random.random()
                        if(rand < regenOdds):
                            newRegens += 1
                    self.failedUnits[j] -= newRegens
    