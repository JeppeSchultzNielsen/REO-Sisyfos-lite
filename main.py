from Simulation import Simulation
from DataHolder import DataHolder

dh = DataHolder(2040,2009)

sim = Simulation(2040,2009,"results/FirstSim.txt", True, dh)
sim.RunSimulation(0,10)