from Simulation import Simulation
from DataHolder import DataHolder
from Options import Options

dh = DataHolder(2040,1985,"data/outage/Plan2040.csv")
options = Options()
options.usePlannedDownTime = True
options.useUnplannedDownTime = True
options.demFlexTransport = 0.3 #these numbers are taken from the tabels at A189 in "Demand" in SisyfosData - defaults are 2030 numbers
options.demFlexCVP = 1
options.demFlexPtX = 1
options.demFlexKlassisk = 0.
options.energyIslandEast = False
options.energyIslandWest = False


sim = Simulation(options, dh, 2040,1985,"results/NewDemand40YesEI.txt", True)
sim.RunSimulation(0,100)