import numpy as np
from Area import Area
from AreaDK import AreaDK
from Line import Line
from pulp import LpMaximize, LpProblem, LpStatus, lpSum, LpVariable, LpMinimize, GLPK_CMD
from DataHolder import DataHolder
from Options import Options
import random
import time

class Simulation:
    def __init__(self, options: Options, dh: DataHolder, asaveFilePath: str, asaving: bool = True, saveDiagnosticsFile: bool = True):
        self.simulationYear = options.simulationYear
        self.climateYear = options.climateYear
        self.saveFilePath = asaveFilePath
        self.saving = asaving

        self.dh = dh
        self.options = options

        #list of names of all areas
        self.nameList = dh.names

        #list to contain all areas
        self.areaList = np.empty(shape=len(self.nameList), dtype = Area)

        #list with demands of all areas
        self.demandList = np.zeros(len(self.nameList))

        #list of productions in all areas
        self.productionList = np.zeros(len(self.nameList))
        self.variableProductionList = np.zeros(len(self.nameList))

        #how much production has "already been used" when doing simulations i multiple steps.
        self.alreadyUsed = np.zeros(len(self.nameList))

        #initialize the lists
        for i in range(len(self.nameList)):
            if(self.nameList[i] == "DK1" or self.nameList[i] == "DK2"):
                self.areaList[i] = (AreaDK(options, dh, self.nameList[i],i))
            else:
                self.areaList[i] = (Area(options, dh, self.nameList[i],i))

        self.numberOfLines = self.GetNumberOfLines()

        #list of all lines
        self.linesList = np.empty(shape=self.numberOfLines, dtype = Line)


        #initialize the lines
        self.fromIndeces = 0
        self.toIndeces = 0
        self.fromLength = 0
        self.toLength = 0
        self.InitializeLines()
        self.InitializeToFrom()
        self.indexArray = np.empty(2*self.numberOfLines,dtype=int)
        for i in range(2*self.numberOfLines):
            self.indexArray[i]=i

        #list to store the value transfered on each line
        self.transferList = np.zeros(self.numberOfLines)

        #we wish to know how much production there is of each type in each node.
        self.productionTypeNames = []
        self.variableProductionNames = []
        self.nonVariableProductionNames = []
        longestProd = 0
        for area in self.areaList:
            self.productionTypeNames.append(area.totProductionNames)
            self.variableProductionNames.append(area.productionNames)
            self.nonVariableProductionNames.append(area.nonTDProductionNames)   
            if(len(area.productionNames) > longestProd):
                longestProd = len(area.totProductionNames)
        self.productionTypeMatrix = np.zeros([len(self.areaList),longestProd])

        #create file for saving output
        if(self.saving):
            self.fileOut = open(self.saveFilePath, "w+")
            #create header
            self.fileOut.write("hour"+"\t")
            for i in range(len(self.nameList)):
                name = self.nameList[i]
                self.fileOut.write(name + "_" + "demand" + "\t")
                self.fileOut.write(name + "_" + "surplus" + "\t")
                self.fileOut.write(name + "_" + "EENS" + "\t")
                for prodname in self.productionTypeNames[i]:
                    self.fileOut.write(prodname + "\t")
                self.fileOut.write(name + "_"+"plannedOutage" + "\t")
                self.fileOut.write(name + "_"+"unplannedOutage" + "\t")
            for line in self.linesList:
                self.fileOut.write(line.GetName() + "\t")
            for line in self.linesList:
                self.fileOut.write(line.GetName() +"_units"+ "\t")
        
        if(saveDiagnosticsFile):
            diagFile = open(self.saveFilePath[:-4]+"Diag.txt", "w+")
            diagFile.write("Information about parameters in run for file " + self.saveFilePath+"\n")
            diagFile.write("Options: \n")
            diagFile.write("Simulation year: " + str(self.simulationYear) + "\n")
            diagFile.write("Climate year: " + str(self.climateYear) + "\n")
            diagFile.write("TYNDP report: " + str(dh.demandYear) + "\n")
            diagFile.write("UsePlannedDownTime: " + str(options.usePlannedDownTime) + "\n")
            diagFile.write("UseUnplannedDownTime: " + str(options.useUnplannedDownTime) + "\n")
            diagFile.write("demFlexKlassisk: " + str(options.demFlexKlassisk) + "\n")
            diagFile.write("demFlexCVP: " + str(options.demFlexCVP) + "\n")
            diagFile.write("demFlexPtX: " + str(options.demFlexPtX) + "\n")
            diagFile.write("demFlexTransport: " + str(options.demFlexTransport) + "\n")
            diagFile.write("Storebaelt2: " + str(options.storebaelt2) + "\n")
            diagFile.write("oresundOpen: " + str(options.oresundOpen) + "\n")
            diagFile.write("EnergyIslandEast: " + str(options.energyIslandEast) + "\n")
            diagFile.write("EnergyIslandWest: " + str(options.energyIslandWest) + "\n")


            for i in range(len(self.areaList)):
                diagFile.write(self.areaList[i].name+"\n")
                diagFile.write(self.areaList[i].GetDiagString()+"\n")

                diagFile.write("\n")

            diagFile.write("Lines: \n")
            diagFile.write("Name\tCapAB\tcapBA\tnoUnits\tDowntime\tDowntimeDuration\n")
            for i in range(len(self.linesList)):
                diagFile.write(str(self.linesList[i].name) +"\t"+str(self.linesList[i].maxCapAB)+"\t"+str(self.linesList[i].maxCapBA)+
                               "\t"+str(self.linesList[i].noUnits)+"\t"+str(self.linesList[i].failureProb)
                               +"\t"+str(self.linesList[i].avgDowntime)+"\n")
                




    #helper function for initializing all lines
    def InitializeLines(self):
        f = open("data/linedata"+str(self.simulationYear)+".csv","r")
        line = f.readline() #skip header
        line = f.readline() #read 1st line
        i = 0
        usedNames = []
        while(line):
            splitted = line.rstrip().split(",")
            linename = splitted[0]
            name = splitted[1] + "_to_" + splitted[2]
            trialName = splitted[1] + "_to_" + splitted[2]
            
            uniqueNameNotFound = True
            noTries = 0

            while(uniqueNameNotFound):
                if(usedNames.count(trialName) == 0):
                    uniqueNameNotFound = False
                    name=trialName
                else:
                    noTries += 1
                    trialName = name + "_" + str(noTries)

            #all sorts of conditions according to the Sisyfos5Data lines sheet.
            if(self.options.storebaelt2 and linename == "Storebaelt"):
                self.linesList[i] = (Line(self.dh,splitted[1],splitted[2],float(splitted[3])*2,float(splitted[4])*2,name, int(splitted[5]), float(splitted[6]), int(splitted[7])))
            elif(linename == "oeresund1-2"):
                if(self.options.oresundOpen):
                    self.linesList[i] = (Line(self.dh,splitted[1],splitted[2],1500*2/3,1300*2/3,name, int(splitted[5]), float(splitted[6]), int(splitted[7])))
                else:
                    self.linesList[i] = (Line(self.dh,splitted[1],splitted[2],0,0,name, int(splitted[5]), float(splitted[6]), int(splitted[7])))
            elif(linename == "oeresund3-4"):
                if(self.options.oresundOpen):
                    self.linesList[i] = (Line(self.dh,splitted[1],splitted[2],1500/3,1300*1/3,name, int(splitted[5]), float(splitted[6]), int(splitted[7])))
                else:
                    self.linesList[i] = (Line(self.dh,splitted[1],splitted[2],0,0,name, int(splitted[5]), float(splitted[6]), int(splitted[7])))
            elif(linename == "oeresund1"):
                if(self.options.oresundOpen):
                    self.linesList[i] = (Line(self.dh,splitted[1],splitted[2],0,0,name, int(splitted[5]), float(splitted[6]), int(splitted[7])))
                else:
                    self.linesList[i] = (Line(self.dh,splitted[1],splitted[2],15/13*400,400,name, int(splitted[5]), float(splitted[6]), int(splitted[7])))
            elif(linename == "oeresund1"):
                if(self.options.oresundOpen):
                    self.linesList[i] = (Line(self.dh,splitted[1],splitted[2],0,0,name, int(splitted[5]), float(splitted[6]), int(splitted[7])))
                else:
                    self.linesList[i] = (Line(self.dh,splitted[1],splitted[2],15/13*400,400,name, int(splitted[5]), float(splitted[6]), int(splitted[7])))
            elif(self.options.energyIslandWest and linename == "EnergyIsland-DK1"):
                self.linesList[i] = (Line(self.dh,splitted[1],splitted[2],1400,1400,name, int(splitted[5]), float(splitted[6]), int(splitted[7])))
            elif(self.options.energyIslandWest and linename == "EnergyIsland-BE"):
                self.linesList[i] = (Line(self.dh,splitted[1],splitted[2],2000,2000,name, int(splitted[5]), float(splitted[6]), int(splitted[7])))
            elif(self.options.energyIslandEast and linename == "Bornholm-DK2"):
                self.linesList[i] = (Line(self.dh,splitted[1],splitted[2],1200,1200,name, int(splitted[5]), float(splitted[6]), int(splitted[7])))
            elif(self.options.energyIslandEast and linename == "Bornholm-DE"):
                    self.linesList[i] = (Line(self.dh,splitted[1],splitted[2],2000,2000,name, int(splitted[5]), float(splitted[6]), int(splitted[7])))
            else:
                #default; for hardcoded lines that have same value independent of year
                self.linesList[i] = (Line(self.dh,splitted[1],splitted[2],float(splitted[3]),float(splitted[4]),name, int(splitted[5]), float(splitted[6]), int(splitted[7])))
            line = f.readline() #read next line
            usedNames.append(name)
            i = i+1

    def InitializeToFrom(self):
        self.fromIndeces = np.zeros((len(self.nameList),30),dtype = 'int')
        self.toIndeces = np.zeros((len(self.nameList),30),dtype = 'int')
        self.fromLength = np.zeros((len(self.nameList)),dtype = 'int')
        self.toLength = np.zeros((len(self.nameList)),dtype = 'int')
        F_index = 0

        for i in range(len(self.linesList)):
            aIndex = self.linesList[i].aIndex
            bIndex = self.linesList[i].bIndex
            self.toIndeces[bIndex][self.toLength[bIndex]]=F_index
            self.fromIndeces[aIndex][self.toLength[aIndex]]=F_index
            self.toLength[bIndex] += 1
            self.fromLength[aIndex] += 1

            self.toIndeces[aIndex][self.toLength[aIndex]]=F_index+1
            self.fromIndeces[bIndex][self.fromLength[bIndex]]=F_index+1
            self.toLength[aIndex] += 1
            self.fromLength[bIndex] += 1
            F_index += 2

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
        for i in range(len(self.areaList)):
            area = self.areaList[i]
            area.PrepareHour(hour)
            self.alreadyUsed = np.zeros(len(self.nameList))
            totalProduction = 0
            totalVarProd = 0

            for j in range(len(self.productionTypeNames[i])):
                prod = area.GetProduction(hour, j)
                totalProduction += prod

                self.productionTypeMatrix[i][j] = prod
                if(j < len(self.areaList[i].productionList)):
                    totalVarProd += prod

            self.productionList[i] = totalProduction
            self.variableProductionList[i] = totalVarProd
            self.demandList[i] = area.GetDemand(hour)

        #reset transferList
        for i in range(len(self.transferList)):
            #reset transferlist
            self.transferList[i] = 0
        
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

            currentPlanned = 0
            currentUnplanned = 0
            for j in range(len(self.productionTypeNames[i])):
                self.fileOut.write(f"{self.productionTypeMatrix[i][j]:.3f}" + "\t")
                currentPlanned += self.areaList[i].totProductionList[j].GetCurrentPlannedOutage()
                currentUnplanned += self.areaList[i].totProductionList[j].GetCurrentUnplannedOutage()


            self.fileOut.write(f"{currentPlanned}" + "\t")
            self.fileOut.write(f"{currentUnplanned}" + "\t")
            i += 1
        i = 0
        for line in self.linesList:
            self.fileOut.write(f"{self.transferList[i]:.3f}" + "\t")
            i += 1
        for line in self.linesList:
            self.fileOut.write(f"{line.noUnits - line.failedUnits}" + "\t")




    #solves the MaxFlow problem under current conditions. 
    def SolveMaxFlowProblem(self):
        #now, solve Maxflow Problem. I suspect that Pulp likes to minimize all variables from the start, and then adjusts the model until
        #solution is found. Therefore there is asymmetry as the "direction" of a line impacts the
        #results. Therefore all lines should be seperated, such that for example the "DK1_to_DK2" line have both "DK1_to_DK2" and "DK2_to_DK1".
        F_vec = np.empty(shape=2*self.numberOfLines, dtype = LpVariable)
        shuffledNames = self.indexArray.copy()
        np.random.shuffle(shuffledNames)
    
        F_index = 0

        for i in range(len(self.linesList)):
            #the variables are stored in pulp alphabetically, therefore should randomize first 3 letters of name. 
            #the "a" is necessary because pulp gets confused if variable names start with numbers
            varname = "a" + f"{shuffledNames[F_index]:03}" + self.linesList[i].GetName()
            F_vec[F_index] = LpVariable(name= varname, lowBound = 0, upBound = self.linesList[i].currentAB)

            varname = "a" + f"{shuffledNames[F_index+1]:03}" + self.linesList[i].GetName() + "_rev"
            F_vec[F_index+1] = LpVariable(name= varname, lowBound = 0, upBound = self.linesList[i].currentBA)
            F_index += 2


        #create model
        model = LpProblem(name="maxFlow", sense=LpMaximize)
        obj_func = 0

        #find demand and production in each node. 
        for i in range(len(self.nameList)):
            hasSurplus = True
            surplus = self.productionList[i] - self.demandList[i] - self.alreadyUsed[i]
            if(surplus < 0):
                hasSurplus = False
            
            build = 0

            for j in range(self.fromLength[i]):
                index = self.fromIndeces[i][j]
                build -= F_vec[index]
                index = self.toIndeces[i][j]
                build += F_vec[index]

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
        #model_begin = time.time()
        status = model.solve(GLPK_CMD(msg=False))
        #print(f"Solve model took {time.time() - model_begin}")

        #save line output 
        F_index = 0
        variableList = model.variables()

        #sometimes, for unknown reasons, a variable called "__dummy" is put in at the front. Remove it.
        dLen = len(variableList) - len(F_vec)
        variableList = variableList[dLen:]

        for i in range(len(self.linesList)):
            nonRevValue = variableList[shuffledNames[F_index]].value()
            revValue = variableList[shuffledNames[F_index+1]].value()

            self.transferList[i] += nonRevValue
            self.transferList[i] -= revValue
            F_index += 2






    def SolveMaxFlowProblemStep1(self):
        F_vec = np.empty(shape=2*self.numberOfLines, dtype = LpVariable)
        shuffledNames = self.indexArray.copy()
        np.random.shuffle(shuffledNames)
    
        F_index = 0

        for i in range(len(self.linesList)):
            varname = "a" + f"{shuffledNames[F_index]:03}" + self.linesList[i].GetName()
            F_vec[F_index] = LpVariable(name= varname, lowBound = 0, upBound = self.linesList[i].currentAB)

            varname = "a" + f"{shuffledNames[F_index+1]:03}" + self.linesList[i].GetName() + "_rev"
            F_vec[F_index+1] = LpVariable(name= varname, lowBound = 0, upBound = self.linesList[i].currentBA)
            F_index += 2

        model = LpProblem(name="maxFlow", sense=LpMaximize)
        obj_func = 0

        for i in range(len(self.nameList)):
            hasSurplus = True
            hasVarSurplus = True
            surplus = self.productionList[i] - self.demandList[i] - self.alreadyUsed[i]
            variableSurplus = self.variableProductionList[i] - self.demandList[i] - self.alreadyUsed[i]
            if(surplus < 0):
                hasSurplus = False
            if(variableSurplus < 0):
                hasVarSurplus = False
            else:
                surplus = variableSurplus


            if(hasSurplus and not hasVarSurplus):
                #Hack to keep out nodes that only has surplus but not variable surplus.
                surplus = 0

            build = 0

            for j in range(self.fromLength[i]): 
                index = self.fromIndeces[i][j]
                build -= F_vec[index]
                index = self.toIndeces[i][j]
                build += F_vec[index]

            if(hasSurplus):
                #if there is surplus, the flow out of the node should not be greater than the surplus.
                model += (-build <= surplus, "constraint_demand_" + self.nameList[i])
                #also, the flow into the node should not be greater than 0.
                model += (build <= 0, "constraint_demand_0_" + self.nameList[i])
            else:
                #if there is not varSurplus, the flow into the node should not be greater than the demand.
                model += (build <= -surplus, "constraint_demand_" + self.nameList[i])
                #also, the flow out of the node should not be greater than 0.
                model += (-build <= 0, "constraint_demand_0_" + self.nameList[i])
                #also the total flow into the node should be maximized
                obj_func += build
    
        #create objective for model
        model += obj_func

        #solve model
        #model_begin = time.time()
        status = model.solve(GLPK_CMD(msg=False))
        #print(f"Solve model took {time.time() - model_begin}")

        #save line output 
        F_index = 0
        variableList = model.variables()

        #sometimes, for unknown reasons, a variable called "__dummy" is put in at the front. Remove it.
        dLen = len(variableList) - len(F_vec)
        variableList = variableList[dLen:]

        for i in range(len(self.linesList)):
            nonRevValue = variableList[shuffledNames[F_index]].value()
            revValue = variableList[shuffledNames[F_index+1]].value()

            self.transferList[i] += nonRevValue
            self.transferList[i] -= revValue
            F_index += 2

    def readjustParams(self):
        for i in range(len(self.transferList)):
            transfer = self.transferList[i]
            fromInd = self.linesList[i].aIndex
            toInd = self.linesList[i].bIndex
            self.alreadyUsed[fromInd] += transfer
            self.alreadyUsed[toInd] -= transfer
            if(transfer > 0):
                self.linesList[i].currentAB = self.linesList[i].hourAB - transfer #we already used som capacity in this direction
            else:
                self.linesList[i].currentBA = self.linesList[i].hourBA + transfer #we already used som capacity in this direction




    def SolveMaxFlowProblemStep3(self):
        F_vec = np.empty(shape=2*self.numberOfLines, dtype = LpVariable)
        shuffledNames = self.indexArray.copy()
        np.random.shuffle(shuffledNames)
    
        F_index = 0

        for i in range(len(self.linesList)):
            varname = "a" + f"{shuffledNames[F_index]:03}" + self.linesList[i].GetName()
            F_vec[F_index] = LpVariable(name= varname, lowBound = 0, upBound = self.linesList[i].currentAB)

            varname = "a" + f"{shuffledNames[F_index+1]:03}" + self.linesList[i].GetName() + "_rev"
            F_vec[F_index+1] = LpVariable(name= varname, lowBound = 0, upBound = self.linesList[i].currentBA)
            F_index += 2

        model = LpProblem(name="maxFlow", sense=LpMaximize)
        obj_func = LpVariable(name= "__dummy", lowBound = 0)

        for i in range(len(self.nameList)):
            hasSurplus = True
            hasVarSurplus = True
            surplus = self.productionList[i] - self.demandList[i] - self.alreadyUsed[i]
            variableSurplus = self.variableProductionList[i] - self.demandList[i] - self.alreadyUsed[i]
            if(surplus < 0):
                hasSurplus = False
            if(variableSurplus < 0):
                hasVarSurplus = False


            build = []

            for j in range(self.fromLength[i]): 
                index = self.fromIndeces[i][j]
                build -= F_vec[index]
                index = self.toIndeces[i][j]
                build += F_vec[index]

            if(hasVarSurplus):
                #if there is surplus, the flow out of the node should not be greater than the surplus.
                model += (-build <= variableSurplus, "constraint_demand_" + self.nameList[i])
                #also, the flow into the node should not be greater than 0.
                model += (build <= 0, "constraint_demand_0_" + self.nameList[i])
            else:
                #if there is not varSurplus, the flow into the node should not be greater than the demand.
                model += (build <= -variableSurplus, "constraint_demand_" + self.nameList[i])
                #also, the flow out of the node should not be greater than 0.
                model += (-build <= 0, "constraint_demand_0_" + self.nameList[i])
                #also the total flow into the node should be maximized
    
        #create objective for model
        model += obj_func
        #solve model
        #model_begin = time.time()
        status = model.solve(GLPK_CMD(msg=False))
        #print(f"Solve model took {time.time() - model_begin}")

        #save line output 
        F_index = 0
        variableList = model.variables()

        #sometimes, for unknown reasons, a variable called "__dummy" is put in at the front. Remove it.
        dLen = len(variableList) - len(F_vec)
        variableList = variableList[dLen:]

        for i in range(len(self.linesList)):
            nonRevValue = variableList[shuffledNames[F_index]].value()
            revValue = variableList[shuffledNames[F_index+1]].value()

            self.transferList[i] += nonRevValue
            self.transferList[i] -= revValue
            F_index += 2


    #Running the simulation
    def RunSimulation(self, beginHour: int, endHour: int):
        #prev_time = time.time()
        if(not self.options.prioritizeVariableProduction):
            for i in range(beginHour, endHour):
                #start_time = time.time()
                if(i%100 == 0):
                    print(f"{self.saveFilePath}: starting hour {i}")
                self.PrepareHour(i)
                #prep_time = time.time()
                #print(f"Prepare hour took {prep_time-start_time}")
                self.SolveMaxFlowProblem()
                #solve_time = time.time()
                #print(f"Solve maxflow took {solve_time-prep_time}")
                if(self.saving):
                    self.SaveData(i)
                #ave_time = time.time()
                #print(f"Save took {save_time-solve_time}")
                #print(f"Total time is {time.time()-prev_time}")
                #prev_time = time.time()
        else:
            for i in range(beginHour, endHour):
                if(i%1 == 0):
                    print(f"{self.saveFilePath}: starting hour {i}")
                #priority is still to have minimal EENS. Therefore solve first problem by maximizing flow of variable production to nodes which are in need. 
                self.PrepareHour(i)
                self.SolveMaxFlowProblemStep1()
                #readjust model parameters becomes some capacity has already been used
                self.readjustParams()
                #priority is still to have minimal EENS. Therefore solve then problem by maximizing flow of total production to nodes which are in need. 
                #run model again, this time to maximize use of renewables.
                self.SolveMaxFlowProblem()
                self.readjustParams()
                #now maximize use of "uregulerbar produktion". 
                self.SolveMaxFlowProblemStep3()

                if(self.saving):
                    self.SaveData(i)


        if(self.saving):
            self.fileOut.close()