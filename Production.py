import numpy as np

class Production:
    def __init__(self):
        pass
        self.maxValue = 0
        self.currentValue = 0
        self.capacityList = []
        self.unplannedOutageList = []
        self.plannedOutageList = []
        self.outageTimeList = []
        self.heatDependenceList = []

        self.unplannedOutageArray = 0
        self.capacityArray = 0

    def GetCurrentValue(self):
        return np.sum(self.capacityArray)

    def AddProducer(self,capacity: float, unplannedOutage: float, plannedOutage: float, outageTime: int, heatDependence: float):
        self.capacityList.append(capacity)
        self.unplannedOutageList.append(unplannedOutage)
        self.plannedOutageList.append(plannedOutage)
        self.outageTimeList.append(outageTime)
        self.heatDependenceList.append(heatDependence)

    def CreateArrays(self):
        self.capacityArray = np.array(self.capacityList)


    
