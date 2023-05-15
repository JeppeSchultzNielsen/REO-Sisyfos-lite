import numpy as np

class PostProcessor:
    def __init__(self):
        self.priorityList = ["ROR",
                             "PR",
                             "RS",
                             "MustRun",
                             "Wind",
                             "Solar",
                             "ICHP",
                             "OtherRE",
                             "OtherRes_NO",
                             "OtherRes_NOn",
                             "OtherRes_DELU",
                             "OtherRes_AT",
                             "OtherRes_NL",
                             "OtherRes_FR",
                             "OtherRes_GB",
                             "OtherRes_BE",
                             "OtherRes_CH",
                             "OtherRes_IT",
                             "HydroRes",
                             "Biofuels",
                             "CKV_EX",
                             "KYV22",
                             "CKV_BP",
                             "CKV_GT",
                             "CKV_DI",
                             "CKV_affald",
                             "DKV_affald",
                             "DKV_bio",
                             "DKV_CC",
                             "DKV_GT",
                             "DKV_GM",
                             "Regulerkraft",
                             "Nuclear",
                             "NuclearSweden",
                             "NuclearFinland",
                             "Kernekraft_DE",
                             "Borssele",
                             "NuclearGB",
                             "NuclearFR",
                             "NuclearBE",
                             "NuclearES",
                             "NuclearCH",
                             "NuclearCZSK",
                             "NuclearHU",
                             "OtherNONRE",
                             "OtherNonRes_NO",
                             "OtherNonRes_AT",
                             "OtherNonRes_NL",
                             "OtherNonRes_GB",
                             "OtherNonRes_FR",
                             "OtherNonRes_BE",
                             "OtherNonRes_CH",
                             "OtherNonRes_EELVLT",
                             "Peat",
                             "GasUdland",
                             "KulUdland",
                             "OlieUdland",
                             "HydroPumpOL",
                             "HydroPumpCL",
                             "Battery",
                             "DSR"]#this list must contain all types givein in the outageParams file
        self.names = ["DK1", "DK2", "DKBO", "DKKF", "DKEI", "NOn","NOm","NOs","SE1","SE2","SE3","SE4","FI","DELU","AT","NL","GB","FR","BE","ESPT","CH","IT","EELVLT", "PL", "CZSK","HU"]

    def process(self, toProcess: str, writeTo: str):
        nodes = []
        for i in range(len(self.names)):
            nodes.append(Node(self.names[i]))

        f = open(toProcess,"r")
        w = open(writeTo,"w")
        header = f.readline()
        w.write(header)

        splittedHeader = header.split("\t")
        for i in range(len(nodes)):
            nodes[i].readHeader(splittedHeader)
        
        moreTxt = True
        lineNo = 0
        while(moreTxt):
            if(lineNo%1000 == 0):
                print("Post processing " + toProcess +": line " + str(lineNo))
            line = f.readline()
            moreTxt = line
            if(not moreTxt): 
                continue
            splittedLine = line.rstrip().split("\t")
            for node in nodes:
                node.readHour(splittedLine)
                node.adjustProduction()
                for i in range(len(node.prodIndexesInHeader)):
                    splittedLine[node.prodIndexesInHeader[i]] = f"{node.shouldBe[node.prodIndexesInValues[i]]:.7f}"
            toWrite = ""
            for i in range(len(splittedLine)):
                toWrite += splittedLine[i]+"\t"
            toWrite +="\n"
            w.write(toWrite)
            lineNo += 1


class Node: 
    def __init__(self, name):
        self.currentHourValues = np.zeros(len(PostProcessor().priorityList))
        self.prodIndexesInHeader = []
        self.prodIndexesInValues = []
        self.priorityList = PostProcessor().priorityList
        self.shouldBe = np.zeros(len(self.priorityList))
        self.toIndeces = []
        self.fromIndeces = []
        self.currentNetImport = 0
        self.demandIndex = -1
        self.demandValue = 0
        self.name = name

    def readHeader(self, splittedHeader):
        for i in range(len(splittedHeader)):
            spl = splittedHeader[i].rstrip().split("_")
            if(len(spl) < 2):
                continue
            if(spl[1] == "to"):
                #this is a line
                if(spl[-1] == "units"):
                    continue
                if(spl[0] == self.name):
                    self.fromIndeces.append(i)
                if(spl[2] == self.name):
                    self.toIndeces.append(i)
            else:
                #this is not a line
                if(spl[0] == self.name):
                    if(spl[1] in ("EENS","surplus","plannedOutage","unplannedOutage","varSurplus","netImport")):
                       continue
                    if(spl[1] == "demand"):
                       self.demandIndex = i
                    else:
                        #it's a type of production. Join the string after node name again. 
                        prodName = spl[1]
                        for j in range(len(spl)-2):
                            prodName += "_"+spl[j+2]
                        found = False
                        for j in range(len(self.priorityList)):
                            if(prodName == self.priorityList[j]):
                                found = True
                                self.prodIndexesInHeader.append(i)
                                self.prodIndexesInValues.append(j)
                        if(not found):
                            print("Error: did not expect " + splittedHeader[i])

    def readHour(self, splittedLine):
        self.demandValue = float(splittedLine[self.demandIndex])
        for i in range(len(self.prodIndexesInHeader)):
            self.currentHourValues[self.prodIndexesInValues[i]] = float(splittedLine[self.prodIndexesInHeader[i]])

        self.currentNetImport = 0
        for i in range(len(self.toIndeces)):
            self.currentNetImport += float(splittedLine[self.toIndeces[i]])
            #print(splittedLine[self.toIndeces[i]])

        for i in range(len(self.fromIndeces)):
            self.currentNetImport -= float(splittedLine[self.fromIndeces[i]])
            #print(splittedLine[self.fromIndeces[i]])

    def adjustProduction(self):
        target = (self.demandValue - self.currentNetImport)
        sum = 0
        for i in range(len(self.shouldBe)):
            if( (sum + self.currentHourValues[i]) < target):
                self.shouldBe[i] = self.currentHourValues[i]
                sum += self.currentHourValues[i]
            else:
                self.shouldBe[i] = target - sum
                sum += target - sum


