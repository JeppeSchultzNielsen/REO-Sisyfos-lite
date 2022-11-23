import numpy as np
from Area import Area
from Line import Line

class Simulation:
    def __init__(self, asimulationYear: int, aclimateYear: int, asaveFilePath: str, asaving: bool):
        self.simulationYear = asimulationYear
        self.climateYear = aclimateYear
        self.saveFilePath = asaveFilePath
        self.saving = asaving
        self.nameList = ["DK1"]

    def RunSimulation(self, beginHour: int, endHour: int):
        print("running")