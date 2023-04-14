from Simulation import Simulation
from DataHolder import DataHolder
from Options import Options

options = Options()
options.usePlannedDownTime = True
options.useUnplannedDownTime = True
options.demFlexTransport = 0.1 #0 for 2025 grundberegning, 0.1 for 2030, 0.2 for 2035, 0.3 for 2040 these numbers are taken from the tabels at A189 in "Demand" in SisyfosData - defaults are 2030 numbers
options.demFlexCVP = 0.9 #0.7 for 2025, 0.9 for 2030, 0.95 for 2035, 1 for 2040
options.demFlexPtX = 1  #altid 1
options.demFlexKlassisk = 0 #0 for 2025, 0 for 2030, 0.25 for 2035, 0.5 for 2040
options.energyIslandEast = False
options.energyIslandWest = False
options.useVariations = True

dh = DataHolder(2030,1985,2030,"data/outage/Plan2030_1985_variations.csv")
sim = Simulation(options, dh, 2030,1985,"results/2030_1985_test_averages.txt", True)
sim.RunSimulation(0,100)

'''
#run 2030 scenario for all climateyears
climateYears = [1985,1987,1996,2007,2008,2009,2010,2011,2012,2013,2014,2015]
for j in range(len(climateYears)):
    dh = DataHolder(2030,climateYears[j],2030,"data/outage/Plan2030_1985.csv")
    sim = Simulation(options, dh, 2030,climateYears[j],"results/2030_"+str(climateYears[j])+"_.txt", True)
    sim.RunSimulation(0,8760)

'''
'''
#run 2035 scenario a few times
options.demFlexTransport = 0.2
options.demFlexCVP = 0.95
options.demFlexPtX = 1
options.demFlexKlassisk = 0.25
climateYears = [2012,2013,2014,2015]#[1985,1987,1996,2007,2008,2009,2010,2011,
for j in range(len(climateYears)):
    for i in range(2):
        dh = DataHolder(2035,climateYears[j],2030,"data/outage/Plan2035_1985.csv")
        sim = Simulation(options, dh, 2035,climateYears[j],"results/2035_"+str(climateYears[j])+"_"+str(i)+".txt", True)
        sim.RunSimulation(0,8760)
'''