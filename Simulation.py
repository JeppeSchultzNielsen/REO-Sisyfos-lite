import numpy as np
from Area import Area
from AreaDK import AreaDK
from Line import Line
from pulp import LpMaximize, LpProblem, LpStatus, lpSum, LpVariable, LpMinimize, GLPK_CMD
from DataHolder import DataHolder
from Options import Options
import random

class Simulation:
    def __init__(self, options: Options, dh: DataHolder, asimulationYear: int, aclimateYear: int, asaveFilePath: str, asaving: bool):
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

        #list of sum flow in all areas
        self.sumFlowList = np.zeros(len(self.nameList))

        #initialize the lists
        for i in range(len(self.nameList)):
            if(self.nameList[i] == "DK1" or self.nameList[i] == "DK2"):
                self.areaList[i] = (AreaDK(options, dh, self.nameList[i],i,self.simulationYear,self.climateYear))
            else:
                self.areaList[i] = (Area(options, dh, self.nameList[i],i,self.simulationYear,self.climateYear))

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
                self.fileOut.write(name + "_" + "surplus" + "\t")
                self.fileOut.write(name + "_" + "EENS" + "\t")
                for prodName in self.productionTypeNames:
                    self.fileOut.write(name + "_" + prodName + "\t")
                self.fileOut.write(name + "_"+"plannedOutage" + "\t")
                self.fileOut.write(name + "_"+"unplannedOutage" + "\t")
            for line in self.linesList:
                self.fileOut.write(line.GetName() + "\t")




    #helper function for initializing all lines
    def InitializeLines(self):
        f = open("data/linedata"+str(self.simulationYear)+".csv","r")
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

            self.linesList[i] = (Line(splitted[0],splitted[1],float(splitted[2]),float(splitted[3]),name, int(splitted[4]), float(splitted[5]), int(splitted[6])))
            line = f.readline() #read next line
            usedNames.append(name)
            i = i+1

    def GetNumberOfLines(self):
        i = 0
        f = open("data/linedata"+str(self.simulationYear)+".csv","r")
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
            self.fileOut.write(f"{self.demandList[i]:.3f}" + "\t")
            self.fileOut.write(f"{self.productionList[i]-self.demandList[i]:.3f}" + "\t")

            j = 0
            EENS = self.productionList[i]-self.demandList[i]
            for j in range(len(self.linesList)):
                if(name == self.linesList[j].GetA()):
                    EENS -= self.transferList[j]
                if(name == self.linesList[j].GetB()):
                    EENS += self.transferList[j]

            EENS = - EENS
            if(EENS < 0):
                EENS = 0
            self.fileOut.write(f"{EENS:.3f}" + "\t")

            j = 0
            for prodName in self.productionTypeNames:
                self.fileOut.write(f"{self.productionTypeMatrix[i][j]:.3f}" + "\t")
                j += 1

            self.fileOut.write(f"{self.areaList[i].nonTDProd.GetCurrentPlannedOutage():.3f}" + "\t")
            self.fileOut.write(f"{self.areaList[i].nonTDProd.GetCurrentUnplannedOutage():.3f}" + "\t")
            i += 1
        i = 0
        for line in self.linesList:
            self.fileOut.write(f"{self.transferList[i]:.3f}" + "\t")
            i += 1




    #solves the MaxFlow problem under current conditions. 
    def SolveMaxFlowProblem(self):
        #now, solve Maxflow Problem. I suspect that Pulp likes to minimize all variables from the start, and then adjusts the model until
        #solution is found. Therefore there is assymmetry in the way it is currently defined, as the "direction" of a line impacts the
        #results. Therefore all lines should be seperated, such that for the "DK1_to_DK2" line have both "DK1_to_DK2" and "DK2_to_DK1".
        F_vec = np.empty(shape=2*self.numberOfLines, dtype = LpVariable)
        toVec = np.empty(2*self.numberOfLines, dtype='<U15')
        fromVec = np.empty(2*self.numberOfLines, dtype='<U15')
    
        F_index = 0

        indexMapNonRev = np.empty(self.numberOfLines, dtype='<U31')
        indexMapRev = np.empty(self.numberOfLines, dtype='<U31')

        for i in range(len(self.linesList)):
            #the variables are stored in pulp alphabetically, therefore should randomize first 3 letters of name. 
            #the "a" is necessary because pulp gets confused if variable names start with numbers
            varname = "a" + str(random.randint(0,9)) + str(random.randint(0,9)) + str(random.randint(0,9)) + self.linesList[i].GetName()
            F_vec[F_index] = LpVariable(name= varname, lowBound = 0, upBound = self.linesList[i].GetMaxCapAB())
            toVec[F_index]=self.linesList[i].GetB()
            fromVec[F_index]=self.linesList[i].GetA()
            indexMapNonRev[i] = varname

            varname = "a" + str(random.randint(0,9)) + str(random.randint(0,9)) + str(random.randint(0,9)) + self.linesList[i].GetName() + "_rev"
            F_vec[F_index+1] = LpVariable(name= varname, lowBound = 0, upBound = self.linesList[i].GetMaxCapBA())
            toVec[F_index+1]=self.linesList[i].GetA()
            fromVec[F_index+1]=self.linesList[i].GetB()
            indexMapRev[i] = varname
            F_index += 2


        #create model
        model = LpProblem(name="maxFlow", sense=LpMaximize)
        obj_func = 0

        #find demand and production in each node. 
        for i in range(len(self.demandList)):
            hasSurplus = True
            surplus = self.productionList[i] - self.demandList[i]
            if(surplus < 0):
                hasSurplus = False
            
            build = 0


            for j in range(len(F_vec)):
                if(self.nameList[i] == toVec[j]):
                    #flow is into node
                    build += F_vec[j]
                if(self.nameList[i] == fromVec[j]):
                    #flow is out of node
                    build += -F_vec[j]

            if(hasSurplus):
                #if there is surplus, the flow out of the node should not be greater than the surplus.
                model += (-build <= surplus, "constraint_demand_" + self.nameList[i])
                #also, the flow into the node should not be greater than 0.
                model += (build <= 0, "constraint_demand_0_" + self.nameList[i])
            else:
                #if there is not surplus, the flow into the node should not be greater than the demand.
                model += (build <= -surplus, "constraint_demand_" + self.nameList[i])
                #also, the flow out of the node should not be greater than 0.
                model += (-build <= 0, "constraint_demand_0_" + self.nameList[i])
                #also the total flow into the node should be maximized
                obj_func += build
    
        #create objective for model
        model += obj_func

        #solve model
        status = model.solve(GLPK_CMD(msg=False))

        for i in range(len(self.transferList)):
            #reset transferlist
            self.transferList[i] = 0

        #save line output 
        for i in (range(len(model.variables()))):

            if("dummy" in model.variables()[i].name):
                continue
        
            if(model.variables()[i].value() == 0):
                continue

            if(model.variables()[i].name[-4:] == "_rev"):
                index = np.where(indexMapRev == model.variables()[i].name)[0]
                self.transferList[index] -= model.variables()[i].value()

            else:
                index = np.where(indexMapNonRev == model.variables()[i].name)[0]
                self.transferList[index] += model.variables()[i].value()


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