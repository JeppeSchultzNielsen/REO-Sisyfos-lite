from Simulation import Simulation
from DataHolder import DataHolder

dh = DataHolder(2040,2009,"data/outage/Plan2040.csv")

sim = Simulation(2040,2009,"results/FirstSim.txt", True, dh)
sim.RunSimulation(0,8759)