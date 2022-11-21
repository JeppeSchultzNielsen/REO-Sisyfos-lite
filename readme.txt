Der er en hovedklasse kaldt Simulation. Denne har metoder: 

Constructor(int simulationYear, int climateYear):  

Initialiserer en liste af el-områder som henter data for det givne simulationyear og climateYear 

Initialiserer en liste af deres demands 

Initialiserer en liste af deres capacities 

Initialiserer en liste af alle tilgængelige lines 

 

PrepareHour(int timetal): 

Løber listen igennem af el-områder og beder dem alle om at forberede sig på timen i det givne timetal. 

Efter det, opdater listerne med hvor meget kapacitet der er i hver node, hvor meget demand der er, og  

 

Klasse: El-område 

 

Superklasse: agent 

 

Agent: Line 

 

Agent: Producer 

 

Agent: Producer: VariableProducer 

 

Agent: Producer: BatteryType 