from Simulation import Simulation
from DataHolder import DataHolder
from Options import Options

dh = DataHolder(2040,2009,"data/outage/Plan2040.csv")
options = Options()
options.usePlannedDownTime = True
options.useUnplannedDownTime = False


sim = Simulation(options, dh, 2040,2009,"results/SimTest.txt", True)
sim.RunSimulation(0,10)