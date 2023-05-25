import random
from DataHolder import DataHolder

class Line:
    def __init__(self, dh: DataHolder, a: str, b: str, maxCapAB: float, maxCapBA: float, name: str, noUnits: int, failureProbability: float, avgDowntime: float):
        self.a = a
        self.b = b
        self.aIndex = dh.names.index(a)
        self.bIndex = dh.names.index(b)
        self.maxCapAB = maxCapAB
        self.maxCapBA = maxCapBA
        self.name = name
        self.noUnits = noUnits
        self.failureProb = failureProbability
        self.avgDowntime = avgDowntime

        self.failOdds = failureProbability/(avgDowntime*(1-failureProbability))

        self.failedUnits = 0

        self.currentAB = 0
        self.currentBA = 0
        self.hourAB = 0
        self.hourBA = 0
        newFails = 0

        #initialize line with failed units with some probability
        for i in range(self.noUnits - self.failedUnits):
            #generate number between 0 and 1 - if below failure odds, unit fails. 
            rand = random.random()
            if(rand < failureProbability):
                #print(f"{self.name} failed in hour {hour}")
                newFails += 1
        
        self.failedUnits += newFails


    def PrepareHour(self, hour: int):
        #allow units to fail 
        newFails = 0
        for i in range(self.noUnits - self.failedUnits):
            #generate number between 0 and 1 - if below failure odds, unit fails. 
            rand = random.random()
            if(rand < self.failOdds):
                #print(f"{self.name} failed in hour {hour}")
                newFails += 1
        
        self.failedUnits += newFails

        self.currentAB = self.maxCapAB * (self.noUnits - self.failedUnits)/self.noUnits
        self.hourAB = self.currentAB
        self.currentBA = self.maxCapBA * (self.noUnits - self.failedUnits)/self.noUnits
        self.hourBA = self.currentBA

        #allow units to heal
        regenOdds = 1/self.avgDowntime
        newRegens = 0
        for k in range(self.failedUnits):
            rand = random.random()
            if(rand < regenOdds):
                #print(f"{self.name} healed in hour {hour}")
                newRegens += 1
        self.failedUnits -= newRegens

    def GetName(self):
        return self.name

    def GetA(self):
        return self.a

    def GetB(self):
        return self.b

    def GetMaxCapAB(self):
        return self.currentAB

    def GetMaxCapBA(self):
        return self.currentBA