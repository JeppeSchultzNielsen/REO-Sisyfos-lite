from Simulation import Simulation
from DataHolder import DataHolder
from Options import Options

options = Options(2035,1985)
options.usePlannedDownTime = True
options.useUnplannedDownTime = True
options.energyIslandEast = False
options.energyIslandWest = False
options.useVariations = True
options.tyndpYear = 2030
dh = DataHolder(options,"data/outage/Plan2035_1985_var.csv")
for i in range(10):
    sim = Simulation(options, dh,"results/2035_1985_var_"+str([i])+".txt", True)
    sim.RunSimulation(0,8760)

dh = DataHolder(options,"data/outage/Plan2035_1985_noVar.csv")
for i in range(10):
    sim = Simulation(options, dh,"results/2035_1985_noVar_"+str([i])+".txt", True)
    sim.RunSimulation(0,8760)

dh = DataHolder(options,"data/outage/Plan2035_2009_var.csv")
for i in range(10):
    sim = Simulation(options, dh,"results/2035_2009_var_"+str([i])+".txt", True)
    sim.RunSimulation(0,8760)

dh = DataHolder(options,"data/outage/Plan2035_2009_noVar.csv")
for i in range(10):
    sim = Simulation(options, dh,"results/2035_2009_noVar_"+str([i])+".txt", True)
    sim.RunSimulation(0,8760)

#climateYears = [1985,1987,1996,2007,2008,2009,2010,2011,2012,2013,2014,2015]