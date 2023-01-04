import numpy as np
from Area import Area
from Line import Line
from pulp import LpMaximize, LpProblem, LpStatus, lpSum, LpVariable, LpMinimize, GLPK_CMD
from DataHolder import DataHolder
import random

class Simulation:
    def __init__(self, asimulationYear: int, aclimateYear: int, asaveFilePath: str, asaving: bool, dh: DataHolder):
        self.simulationYear = asimulationYear
        self.climateYear = aclimateYear
        self.saveFilePath = asaveFilePath
        self.saving = asaving

        self.dh = dh

        #list of names of all areas
        self.nameList = dh.names

        #list to contain all areas
        self.areaList = np.empty(shape=len(self.nameList), dtype = Area)

        #list with demands of all areas
        self.demandList = np.zeros(len(self.nameList))

        #list of productions in all areas
        self.productionList = np.zeros(len(self.nameList))

        #initialize the lists
        for i in range(len(self.nameList)):
            self.areaList[i] = (Area(self.nameList[i],i,self.simulationYear,self.climateYear,dh))

        self.numberOfLines = self.GetNumberOfLines()

        #list of all lines
        self.linesList = np.empty(shape=self.numberOfLines, dtype = Line)

        #initialize the lines
        self.InitializeLines()

        #list to store the value transfered on each line
        self.transferList = np.zeros(self.numberOfLines)

        #we wish to know how much production there is of each type in each node.
        self.productionTypeNames = dh.productionTypes
        self.productionTypeMatrix = np.zeros([len(self.nameList), len(self.productionTypeNames)])

        #create file for saving output
        if(self.saving):
            self.fileOut = open(self.saveFilePath, "w+")
            #create header
            self.fileOut.write("hour"+"\t")
            for name in self.nameList:
                self.fileOut.write(name + "_" + "demand" + "\t")
                for prodName in self.productionTypeNames:
                    self.fileOut.write(name + "_" + prodName + "\t")
            for line in self.linesList:
                self.fileOut.write(line.GetName() + "\t")




    #helper function for initializing all lines
    def InitializeLines(self):
        f = open("data\linedata"+str(self.simulationYear)+".csv","r")
        line = f.readline() #skip header
        line = f.readline() #read 1st line
        i = 0
        usedNames = []
        while(line):
            splitted = line.split(",")
            name = splitted[0] + "_to_" + splitted[1]
            trialName = splitted[0] + "_to_" + splitted[1]
            
            uniqueNameNotFound = True
            noTries = 0

            while(uniqueNameNotFound):
                if(usedNames.count(trialName) == 0):
                    uniqueNameNotFound = False
                    name=trialName
                else:
                    noTries += 1
                    trialName = name + "_" + str(noTries)

            self.linesList[i] = (Line(splitted[0],splitted[1],float(splitted[2]),float(splitted[3]),name))
            line = f.readline() #read next line
            usedNames.append(name)
            i = i+1

    def GetNumberOfLines(self):
        i = 0
        f = open("data\linedata"+str(self.simulationYear)+".csv","r")
        line = f.readline() #skip header
        line = f.readline() #read 1st line
        while(line):
            line = f.readline() #read next line
            i = i+1
        return i


    #helper function
    def GetOriginalAreaIndex(self, name: str):
        return self.nameList.index(name, 0, len(self.nameList))




    def PrepareHour(self, hour: int):
        i = 0
        for area in self.areaList:
            area.PrepareHour(hour)
            currentAreaIndex = i
            totalProduction = 0
            j = 0
            for prodType in self.productionTypeNames:
                prod = area.GetProduction(hour, j)
                totalProduction += prod
                self.productionTypeMatrix[i][j] = prod
                j += 1

            self.productionList[i] = totalProduction
            self.demandList[i] = area.GetDemand(hour, currentAreaIndex)

            i += 1

        i = 0
        for line in self.linesList:
            line.PrepareHour(hour)

    

    #writes all current data to the output file
    def SaveData(self, hour: int):
        self.fileOut.write("\n")
        self.fileOut.write(str(hour)+"\t")
        i = 0
        for name in self.nameList:
            self.fileOut.write(str(self.demandList[i]) + "\t")
            j = 0
            for prodName in self.productionTypeNames:
                self.fileOut.write(str(self.productionTypeMatrix[i][j]) + "\t")
                j += 1
            i += 1
        i = 0
        for line in self.linesList:
            self.fileOut.write(str(self.transferList[i]) + "\t")
            i += 1




    #solves the MaxFlow problem under current conditions. 
    def SolveMaxFlowProblem(self):

        #first, create a scrambled list of area names
        scrambledNames = self.nameList.copy()
        random.shuffle(scrambledNames)
        scrambledProductions = np.zeros(len(self.productionList))
        scrambledDemands = np.zeros(len(self.demandList))

        scrambledLines = self.linesList.copy()
        random.shuffle(scrambledLines)

        #create equally shuffled lists of productions and demands
        i = 0
        for name in scrambledNames:
            origIndex = self.GetOriginalAreaIndex(name)
            scrambledProductions[i] = (self.productionList[origIndex])
            scrambledDemands[i] = (self.demandList[origIndex])
            i = i + 1
        
        #now, solve Maxflow Problem
        F_vec = np.empty(shape=self.numberOfLines, dtype = LpVariable)
    
        for i in range(len(scrambledLines)):
            F_vec[i] = LpVariable(name=scrambledLines[i].GetName(), lowBound=-scrambledLines[i].GetMaxCapBA(), upBound = scrambledLines[i].GetMaxCapAB())

        #create model
        model = LpProblem(name="maxFlow", sense=LpMaximize)
        obj_func = 0

        #find demand and production in each node. 
        for i in range(len(scrambledDemands)):
            hasSurplus = True
            surplus = scrambledProductions[i] - scrambledDemands[i]
            if(surplus < 0):
                hasSurplus = False
            build = 0
            #find lines relevant to this node. If they are in index 0, they represent flow out, if they are in index 1, they
            #represent flow in.
            for j in range(len(scrambledLines)):
                if(scrambledNames[i] == scrambledLines[j].GetA()):
                    #positive flow corresponds to flow out of node
                    build -= F_vec[j]
                    if(not hasSurplus):
                        #if node does not have surplus, should maximize flow into node
                        obj_func -= F_vec[j]
                if(scrambledNames[i] == scrambledLines[j].GetB()):
                    #positive flow corresponds to flow into node
                    build += F_vec[j]
                    if(not hasSurplus):
                        #if node does not have surplus, should maximize flow into node
                        obj_func += F_vec[j]

            model += (-build <= surplus, "constraint_demand" + str(i))
    
        #create objective for model
        model += obj_func

        #solve model
        status = model.solve(GLPK_CMD(msg=False))

        #save line output 
        for i in (range(len(scrambledLines))):
            for j in range(len(self.linesList)):
                if(scrambledLines[i].GetName() == self.linesList[j].GetName()):
                    self.transferList[j] = model.variables()[i].value()




    #Running the simulation
    def RunSimulation(self, beginHour: int, endHour: int):
        for i in range(beginHour, endHour):
            print("Starting hour " + str(i))
            self.PrepareHour(i)
            self.SolveMaxFlowProblem()
            if(self.saving):
                self.SaveData(i)

        if(self.saving):
            self.fileOut.close()