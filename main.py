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
dh = DataHolder(options,"data/outage/Plan2035_1985_var.csv")

for i in range(2):
    sim = Simulation(options, dh,f"results/2035_1985_{i}.txt", True, False)
    sim.RunSimulation(0,8760)
    pp = PostProcessor()
    pp.process(f"results/2035_1985_{i}.txt",f"results/2035_1985_{i}_pp.txt")

#climateYears = [1985,1987,1996,20På 07,2008,2009,2010,2011,2012,2013,2014,2015]