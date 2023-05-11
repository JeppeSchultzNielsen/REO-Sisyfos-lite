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
                             "OntherNonRes_NO",
                             "OntherNonRes_AT",
                             "OntherNonRes_NL",
                             "OntherNonRes_GB",
                             "OntherNonRes_FR",
                             "OntherNonRes_BE",
                             "OntherNonRes_CH",
                             "OntherNonRes_EELVLT",
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
        node1 = Node("DELU")
        pass
        


class Entry:
    def __init__(self, index):
        self.index = index
        self.positiveTo = float("Nan")
        self.negativeTo = float("Nan")

class Node: 
    def __init__(self, name):
        self.currentHourValues = np.zeros(len(PostProcessor().priorityList))
        self.prodIndexesInheader = []
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
            spl = splittedHeader[i].split("_")
            if(spl[1] == "to"):
                #this is a line
                if(spl[0] == self.name):
                    self.fromIndeces.append(i)
                if(spl[2] == self.name):
                    self.toIndeces.append(i)
            else:
                #this is not a line
                if(spl[0] == self.name):
                    if(spl[1] in ("EENS","surplus","plannedOutage","unplannedOutage")):
                       continue
                    if(spl[1] == "demand"):
                       self.demandIndex = i
                    else:
                        #it's a type of production.
                        found = False
                        for j in range(len(self.priorityList)):
                            if( spl[1] == self.priorityList[j]):
                                found = True
                                self.prodIndexesInheader.append(i)
                                self.prodIndexesInValues.append(j)
                        if(not found):
                            print("Error: did not expect " + splittedHeader[i])


