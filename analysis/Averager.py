import numpy as np

class Averager:
    #pathsToAverage is a list of the paths for the files that are to be averaged (they should be from same climateYear and SimulationYear)
    def Average(pathsToAverage,output):  
            name = pathsToAverage[0]
            f = open(name,"r") 
            print("Averager: reading " + name)
            w = open(output,"w") 
            header = f.readline()
            w.write(header)
            data = np.loadtxt(name, skiprows = 1)
            for i in range(len(pathsToAverage)-1):
                name = pathsToAverage[i+1]
                print("Averager: reading " + name)
                data += np.loadtxt(name, skiprows = 1)
            data = data/len(pathsToAverage)
            print("Averager: saving output to" + output)
            for i in range(len(data)):
                build = ""
                for j in range(len(data[i])):
                      build += (f"{data[i][j]:.3f}" + "\t")
                build += "\n"
                w.write(build)