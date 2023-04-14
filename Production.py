import numpy as np
from Options import Options

class Production:
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
        self.variationColList = []

        self.capacityArray = 0
        self.unplannedOutageArray = 0
        self.plannedOutageArray = 0
        self.outageTimeArray = 0
        self.heatDependenceArray = 0
        self.noUnitsArray = 0
        self.noFunctioningUnitsArray = 0

    def GetCurrentValue(self, hour):
        sum = 0
        for i in range(len(self.capacityArray)):
            sum += self.capacityArray[i] * self.noFunctioningUnitsArray[i] / self.noUnitsArray[i] * self.variationColList[i][hour]
        return sum

    def GetNumberOfPlants(self):
        return len(self.capacityArray)

    def GetNoUnitsArray(self):
        return np.copy(self.noUnitsArray)

    def GetCapacityArray(self):
        return np.copy(self.capacityArray)

    def GetPlannedOutageArray(self):
        return np.copy(self.plannedOutageArray)

    def GetUnplannedOutageArray(self):
        return np.copy(self.unplannedOutageArray)

    def GetOutageTimeArray(self):
        return np.copy(self.outageTimeArray)

    def GetNamesList(self):
        return self.nameList
    

    def AddProducer(self, name: str, capacity: float, noUnits: int, unplannedOutage: float, plannedOutage: float, outageTime: int, heatDependence: float, type: str, variation: str,variationCol: np.array):
        self.nameList.append(name)
        self.capacityList.append(capacity)
        self.unplannedOutageList.append(unplannedOutage)
        self.plannedOutageList.append(plannedOutage)
        self.outageTimeList.append(outageTime)
        self.heatDependenceList.append(heatDependence)
        self.noUnitsList.append(noUnits)
        self.typesList.append(type)
        self.variationList.append(variation)
        self.variationColList.append(variationCol)

    def CreateArrays(self):
        self.capacityArray = np.array(self.capacityList)
        self.unplannedOutageArray = np.array(self.unplannedOutageList)
        self.plannedOutageArray = np.array(self.plannedOutageList)
        self.outageTimeArray = np.array(self.outageTimeList)
        self.heatDependenceArray = np.array(self.heatDependenceList)
        self.noUnitsArray = np.array(self.noUnitsList)
        self.noFunctioningUnitsArray = self.noUnitsArray


    def PrintArrays(self):
        print(self.capacityArray)
        print(self.unplannedOutageArray)
        print(self.plannedOutageArray)
        print(self.outageTimeArray)
        print(self.noUnitsArray)
        print(self.heatDependenceArray)


    
