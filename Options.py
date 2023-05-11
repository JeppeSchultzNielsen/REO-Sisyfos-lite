#options class keeps track of all options 

class Options:
    def __init__(self, simulationYear: int, climateYear: int):
        self.simulationYear = simulationYear
        self.climateYear = climateYear
        self.usePlannedDownTime = True
        self.useUnplannedDownTime = True
        self.demFlexKlassisk = 0
        self.demFlexCVP = 0.9
        self.demFlexPtX = 1
        self.demFlexTransport = 0.1
        self.storebaelt2 = False
        self.oresundOpen = False
        self.energyIslandEast = True
        self.energyIslandWest = True 
        self.useVariations = False #Use variations when making the outageplan. Only relevant when creating a new outageplan. 
        self.tyndpYear = 2030
        self.prioritizeVariableProduction = True
        if(simulationYear == 2025):
            self.demFlexTransport = 0 #0 for 2025 grundberegning, 0.1 for 2030, 0.2 for 2035, 0.3 for 2040 these numbers are taken from the tabels at A189 in "Demand" in SisyfosData - defaults are 2030 numbers
            self.demFlexCVP = 0.7 #0.7 for 2025, 0.9 for 2030, 0.95 for 2035, 1 for 2040
            self.demFlexPtX = 1  #altid 1
            self.demFlexKlassisk = 0 #0 for 2025, 0 for 2030, 0.25 for 2035, 0.5 for 2040
        if(simulationYear == 2030):
            self.demFlexTransport = 0.1 #0 for 2025 grundberegning, 0.1 for 2030, 0.2 for 2035, 0.3 for 2040 these numbers are taken from the tabels at A189 in "Demand" in SisyfosData - defaults are 2030 numbers
            self.demFlexCVP = 0.9 #0.7 for 2025, 0.9 for 2030, 0.95 for 2035, 1 for 2040
            self.demFlexPtX = 1  #altid 1
            self.demFlexKlassisk = 0 #0 for 2025, 0 for 2030, 0.25 for 2035, 0.5 for 2040
        if(simulationYear == 2035):
            self.demFlexTransport = 0.2 #0 for 2025 grundberegning, 0.1 for 2030, 0.2 for 2035, 0.3 for 2040 these numbers are taken from the tabels at A189 in "Demand" in SisyfosData - defaults are 2030 numbers
            self.demFlexCVP = 0.95 #0.7 for 2025, 0.9 for 2030, 0.95 for 2035, 1 for 2040
            self.demFlexPtX = 1  #altid 1
            self.demFlexKlassisk = 0.25 #0 for 2025, 0 for 2030, 0.25 for 2035, 0.5 for 2040
        if(simulationYear == 2040):
            self.demFlexTransport = 0.3 #0 for 2025 grundberegning, 0.1 for 2030, 0.2 for 2035, 0.3 for 2040 these numbers are taken from the tabels at A189 in "Demand" in SisyfosData - defaults are 2030 numbers
            self.demFlexCVP = 1 #0.7 for 2025, 0.9 for 2030, 0.95 for 2035, 1 for 2040
            self.demFlexPtX = 1  #altid 1
            self.demFlexKlassisk = 0.5 #0 for 2025, 0 for 2030, 0.25 for 2035, 0.5 for 2040

    
