class Area:
    def __init__(self, areaName: str, simulationYear: int, climateYear: int):
        self.name = areaName
        self.demands 

    def PrepareHour(self, hour: int):
        pass
    
    def GetName(self):
        return self.name

    #must be able to return the production for a given type for a given hour
    def GetProduction(self, hour: int, type: str):
        return 0

    def GetDemand(self, hour: int):
        return 0