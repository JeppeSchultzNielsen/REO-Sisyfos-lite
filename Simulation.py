import numpy as np
from Area import Area
from Line import Line
from pulp import LpMaximize, LpProblem, LpStatus, lpSum, LpVariable, LpMinimize
import random

class Simulation:
    def __init__(self, asimulationYear: int, aclimateYear: int, asaveFilePath: str, asaving: bool):
        self.simulationYear = asimulationYear
        self.climateYear = aclimateYear
        self.saveFilePath = asaveFilePath
        self.saving = asaving

        #list of names of all areas
        self.nameList = ["DK1", "DK2", "etc"]

        #list to contain all areas
        self.areaList = []

        #list with demands of all areas
        self.demandList = []

        #list of productions in all areas
        self.productionList = []

        #initialize the lists
        for name in self.nameList:
            self.areaList.append(Area(name,self.simulationYear,self.climateYear))
            self.demandList.append(0)
            self.productionList.append(0)

        #list of all lines
        self.linesList = []

        #initialize the lines
        self.InitializeLines()

        #list to store the value transfered on each line
        self.transferList = []

        #initialize the list
        for line in self.linesList:
            self.transferList.append(0)

        #we wish to know how much production there is of each type in each node.
        self.productionTypeNames = ["WS","PV","Nclear","etc"]
        self.productionTypeMatrix = []

        #initialize productionTypeMatrix
        for area in self.areaList:
            productions = []
            for types in self.productionTypeNames:
                productions.append(0)
            self.productionTypeMatrix.append(productions)

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
        pass #bliver noget med self.linesList.append(Line("navnA",navnB osv))




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
                prod = area.GetProduction(hour, prodType)
                totalProduction += prod
                self.productionTypeMatrix[i][j] = prod
                j += 1

            self.productionList[i] = totalProduction
            self.demandList[i] = area.GetDemand(hour)

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
        i = 0
        for line in self.linesList:
            self.fileOut.write(self.transferList[i] + "\t")
            i += 1




    #solves the MaxFlow problem under current conditions. 
    def SolveMaxFlowProblem(self):

        #first, create a scrambled list of area names
        scrambledNames = self.nameList.copy()
        random.shuffle(scrambledNames)
        scrambledProductions = []
        scrambledDemands = []

        scrambledLines = self.linesList.copy()
        random.shuffle(scrambledLines)

        #create equally shuffled lists of productions and demands
        for name in scrambledNames:
            origIndex = self.GetOriginalAreaIndex(name)
            scrambledProductions.append(self.productionList[origIndex])
            scrambledDemands.append(self.demandList[origIndex])
        
        #now, solve Maxflow Problem
        F_vec = []
    
        for i in range(len(scrambledLines)):
            F_vec.append(0)
            F_vec[i] = LpVariable(name="F"+str(i), lowBound=-scrambledLines.GetMaxCapBA(), upBound = scrambledLines.GetMaxCapAB())

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
            j = 0
            for line in range(len(scrambledLines)):
                if(scrambledNames[i] == line.GetA()):
                    #positive flow corresponds to flow out of node
                    build -= F_vec[j]
                    if(not hasSurplus):
                        #if node does not have surplus, should maximize flow into node
                        obj_func -= F_vec[j]
                if(scrambledNames[i] == line.GetB()):
                    #positive flow corresponds to flow into node
                    build += F_vec[j]
                    if(not hasSurplus):
                        #if node does not have surplus, should maximize flow into node
                        obj_func += F_vec[j]

            model += (-build <= surplus, "constraint_demand" + str(i))
            j +=1
    
        #create objective for model
        model += obj_func

        #solve model
        status = model.solve()

        #save line output 
        for i in (range(len(scrambledLines))):
            for j in range(len(self.linesList)):
                if(scrambledLines[i].GetName() == self.linesList[j].GetName()):
                    self.transferList[j] = model.variables()[i].value()




    #Running the simulation
    def RunSimulation(self, beginHour: int, endHour: int):
        for i in range(beginHour, endHour):
            self.PrepareHour(i)
            self.SolveMaxFlowProblem()
            if(self.saving):
                self.SaveData(i)

        if(self.saving):
            self.fileOut.close()