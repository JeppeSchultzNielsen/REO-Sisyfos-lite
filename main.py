from Simulation import Simulation
from DataHolder import DataHolder
from Options import Options

dh = DataHolder(2030,2009,"data/outage/Plan2030.csv")
options = Options()
options.usePlannedDownTime = True
options.useUnplannedDownTime = False


sim = Simulation(options, dh, 2030,2009,"results/NewDemand30.txt", True)
sim.RunSimulation(0,10)

dh = DataHolder(2025,2009,"data/outage/Plan2025.csv")
options = Options()
options.usePlannedDownTime = True
options.useUnplannedDownTime = False


sim = Simulation(options, dh, 2025,2009,"results/NewDemand25.txt", True)
sim.RunSimulation(0,10)