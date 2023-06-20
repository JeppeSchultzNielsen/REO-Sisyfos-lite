import numpy as np
import sys
sys.path.append('../')
from PostProcessor import Node
from PostProcessor import PostProcessor

#denne kode skulle kunne beregne effektiv transfer mellem noder, men den er baseret på en dårlig idé

class EffectiveTransfer:
    def __init__(self, name: str):
        self.name = name
        f = open(name,"r") 
        self.header = f.readline()
        self.splittedHeader = self.header.split()
        self.data = np.transpose(np.loadtxt(name, skiprows = 1))
        self.dataTransposed = np.transpose(self.data)
        self.nodeNames = PostProcessor().names
        self.nodes = []
        for i in range(len(self.nodeNames)):
            self.nodes.append(Node(self.nodeNames[i]))
            self.nodes[i].readHeader(self.splittedHeader)

    #koden skal gå således:
    #opret en stor matrix, der indeholder alle effektive linjer. Opdater den med de værdier, der er i starten. 
    #For hver node, se på eksport og import. Hvis den har både eksport og import, så fordel importen mellem de lande der eksporteres til og juster tilsvarende.
    #bliv ved indtil alle lande er enten 100% eksportører eller 100% importører.

    def StartEffectiveTransfer(self):
        transferMatrices = []
        transferHeaders = []
        netImports = []
        for i in range(len(self.nodeNames)):
            transferMatrix = np.zeros([len(self.nodeNames),8760]) #create matrix to store the effective import
            transferHeader = []
            netImport = np.zeros(8760)
            for name in self.nodeNames:
                transferHeader.append("eff_"+self.nodeNames[i]+"_to_" +name)
            transferMatrices.append(transferMatrix)
            transferHeaders.append(transferHeader)
            netImports.append(netImport)

        for i in range(len(self.nodeNames)):
            netImportIndex = self.splittedHeader.index(self.nodeNames[i]+"_netImport")
            netImports[i] = self.data[netImportIndex]
            for j in range(len(self.nodes[i].fromIndeces)):
                fromIndex = self.nodeNames.index(self.nodes[i].fromNames[j])
                transferMatrices[i][fromIndex] = self.data[self.nodes[i].fromIndeces[j]]
            for j in range(len(self.nodes[i].toIndeces)):
                toIndex = self.nodeNames.index(self.nodes[i].toNames[j])
                transferMatrices[i][toIndex] = -self.data[self.nodes[i].toIndeces[j]]

        for i in range(8760):
            if(i%100 == 0):
                print(f"creating effective transfer: {i/8760*100}%")
            nextHourTransfer = np.zeros([len(self.nodeNames),len(self.nodeNames)])
            convergenceMatrix = np.zeros(len(self.nodeNames),dtype=int)
            notConverged = True
            while(notConverged):
                for j in range(len(self.nodeNames)):
                    #beregn overskuddet i denne node og opdater nextHourTransfer. Se om alle linjer har samme fortegn her; hvis de har, så kan vi ikke gøre mere på denne linje.
                    ownProd = 0
                    sumExports = 0
                    sumImports = 0
                    hasExport = False
                    hasImport = False
                    for k in range(len(self.nodeNames)):
                        nextHourTransfer[j][k] = transferMatrices[j][k][i]
                        ownProd += transferMatrices[j][k][i]
                        if(transferMatrices[j][k][i] > 0.001): 
                            sumExports += transferMatrices[j][k][i]
                            hasExport = True
                            #print(f"exoport: {transferMatrices[j][k][i]}")
                        if(transferMatrices[j][k][i] < -0.001):
                            sumImports += transferMatrices[j][k][i]
                            hasImport = True

                    ownProd = abs(ownProd)
                    sumImports = abs(sumImports)
                    sumExports = abs(sumExports)
                    if(j == 1): 
                        print(transferHeaders[j])
                        print(nextHourTransfer[j])
                    #hvis der både er import og export i denne node, så er der mere arbejde at gøre
                    if(hasImport and hasExport):
                        convergenceMatrix[j] = 1
                        #print(transferHeaders[j])
                        #print(nextHourTransfer[j])
                        #print(sumExports)
                        if(sumExports > sumImports):
                            for k in range(len(self.nodeNames)):
                                if(transferMatrices[j][k][i] > 0):
                                    #dette er eksport. Fordel denne på importen + produktion
                                    exported = transferMatrices[j][k][i]
                                    #så meget export går fra noden selv (den har overskud)
                                    usedExport = exported/sumExports*abs(ownProd)
                                    for l in range(len(self.nodeNames)):
                                        if(transferMatrices[j][l][i] < 0):
                                            #dette er import. 
                                            imported = transferMatrices[j][l][i]
                                            #I det næste skridt af processen skal vi i stedet bare have at denne import (vægtet) går direkte til det land, der eksporterer
                                            effTransfer = abs((exported-usedExport)/(sumExports-ownProd)*imported)
                                            nextHourTransfer[l][k] -= effTransfer
                                            nextHourTransfer[k][l] += effTransfer
                                            nextHourTransfer[j][k] -= effTransfer
                                            nextHourTransfer[j][l] += effTransfer
                        else: 
                            print(sumImports)
                            for k in range(len(self.nodeNames)):
                                if(transferMatrices[j][k][i] < 0):
                                    #dette er import. Fordel denne på eksport + forbrug
                                    imported = abs(transferMatrices[j][k][i])
                                    #så meget import går ind i noden selv (den har underskud)
                                    usedImport = abs(imported/sumImports)*abs(ownProd)
                                    for l in range(len(self.nodeNames)):
                                        if(transferMatrices[j][l][i] > 0):
                                            #dette er export. 
                                            export = transferMatrices[j][l][i]
                                            #I det næste skridt af processen skal vi i stedet bare have at denne import (vægtet) går direkte til det land, der eksporterer
                                            effTransfer = (imported-usedImport)/(sumImports-ownProd)*export
                                            if(j==1): print(f"from {self.nodeNames[k]} To {self.nodeNames[l]} {effTransfer}")
                                            nextHourTransfer[l][k] += effTransfer
                                            nextHourTransfer[k][l] -= effTransfer
                                            nextHourTransfer[j][k] += effTransfer
                                            nextHourTransfer[j][l] -= effTransfer
                    else:
                        #den er converged.
                        convergenceMatrix[j] = 0
                    if(j == 1): 
                        print("After process")
                        print(transferHeaders[j])
                        print(nextHourTransfer[j])

                #inden næste skridt af processen, opdater transfermatricerne med nextHour transfer.
                for j in range(len(self.nodeNames)):
                    for k in range(len(self.nodeNames)):
                        transferMatrices[j][k][i] = nextHourTransfer[j][k]

                if(np.sum(convergenceMatrix) == 0):
                    notConverged = False
        return (transferMatrices,transferHeaders)
    
    def WriteEffectiveTransfers(self, writeTo, transferMatrices,transferHeaders):
        w = open(writeTo,"w")
        line = ""
        for i in range(len(transferHeaders)):
            for j in range(len(transferHeaders[i])):
                line += transferHeaders[i][j]+"\t"

        line += "\n"
        for i in range(8760):
            for j in range(len(transferMatrices)):
                for k in range(len(transferMatrices[j])):
                    line += f"{transferMatrices[j][k][i]:.7f}\t"
            line += "\n"
        w.write(line)


                
        

    def FindEffectiveImport(self, importMatrix, nodeName,hour):
        pass

    def getNode(self,nodeName):
        ind = self.nodeNames.index(nodeName)
        return self.nodes[ind]
