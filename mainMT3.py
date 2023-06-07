from Simulation import Simulation
from DataHolder import DataHolder
from Options import Options
from PostProcessor import PostProcessor

options = Options(2035,1985)
options.usePlannedDownTime = True
options.useUnplannedDownTime = True
options.energyIslandEast = True
options.energyIslandWest = True
options.useVariations = True
options.tyndpYear = 2030
options.prioritizeVariableProduction = True
options.prioritizeNuclear = True
dh = DataHolder(options,"data/outage/Plan2035_1985_var.csv")

for i in [2013,2014,2015]:
    options = Options(2035,i)
    options.usePlannedDownTime = True
    options.useUnplannedDownTime = True
    options.energyIslandEast = True
    options.energyIslandWest = True
    options.useVariations = True
    options.tyndpYear = 2030
    options.prioritizeVariableProduction = True
    options.prioritizeNuclear = True
    dh = DataHolder(options,"data/outage/Plan2035_1985_var.csv")
    for j in range(5):
        sim = Simulation(options, dh,f"results/2035_{i}_{j}_nuPrio.txt", True, False)
        sim.RunSimulation(0,8760)
        pp = PostProcessor()
        pp.process(f"results/2035_{i}_{j}_nuPrio.txt",f"results/2035_{i}_{j}_nuPrio_pp.txt")