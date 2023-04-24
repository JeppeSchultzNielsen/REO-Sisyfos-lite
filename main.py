from Simulation import Simulation
from DataHolder import DataHolder
from Options import Options

options = Options(2035,1985)
options.usePlannedDownTime = True
options.useUnplannedDownTime = True
options.energyIslandEast = True
options.energyIslandWest = True
options.useVariations = True
options.tyndpYear = 2030
dh = DataHolder(options,"data/outage/Plan2035_1985_var.csv")
sim = Simulation(options, dh,"results/2035_1985_test.txt", True)
sim.RunSimulation(0,300)

#climateYears = [1985,1987,1996,2007,2008,2009,2010,2011,2012,2013,2014,2015]