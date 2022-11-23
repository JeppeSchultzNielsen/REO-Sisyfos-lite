Der er en klasse kaldt Simulation, der kører selve simuleringen. simulationYear forstås som året, der simuleres (eks 2030), 
climateYear forstås som året der hentes timeserier fra (eks 2009)
Denne har metoder: 
class Simulation:
__init___(int simulationYear, int climateYear, string saveFile, bool saving):  
Initialiserer en liste af el-områder som henter data for det givne simulationyear og climateYear 
Initialiserer en liste af deres demands 
Initialiserer en liste af deres samlede productioncapacities 
Initialiserer en liste af alle tilgængelige lines
Initialiser en liste til at holde på de transmissioner, der beregnes i SolveMaxFlow()
Initialisér lister for hver node, der holder på produktionstyperne i den gældende node
Initialiser saveFile, en path til den fil, der kommer til at indeholde data efter run.
Initialiser saving, en bool der siger om simuleringsdataet skal skrives i en txt fil. 
Hvis saving, skab en txt-fil der kan indeholde data, og lav en header i denne fil.

PrepareHour(int hour): 
Løber listen igennem af el-områder og beder dem alle om at forberede sig på timen i det givne timetal. 
Efter det, opdater listerne med hvor meget kapacitet der er i hver node, hvor meget demand der er, og hvilke lines der er tilgængelige. 

SolveMaxFlow():
Under de parametre, der er blevet opdateret i PrepareHour(), løs Maxflow problemet. Scrambl rækkefølgen af nodes inden?

SaveData():
Append en linje til txt-filen med dataen for den pågældende time.

RunSimulation(int beginHour, int endHour):
Kører simulationen fra begyndelsestimen til endtimen (dvs 0 til 8760 hvis man vil køre hele året) ved at gøre følgende i et for-loop:
PrepareHour() for den pågældende time
SolveMaxFlow()
Der skal være en prioriteringsliste af, hvad man slukker for først, når man har overskud man ikke kan komme af med. Man slukker så for produktionen 
i værker i noden indtil der ikke længere er overskud af strøm i noden (ifht transmission og demand) 
Hvis saving, SaveData()



Area klassen simulerer et el-pris-område som f.eks. DK-øst
Class: Area
__init___(string name, int simulationYear, int climateYear):
Indhenter værdierne for produktion i forskellige værkstyper i simuleringsåret. Og også demand. 
Indhenter timeserier for området

GetDemand(int hour):
Returnér demand i den pågældende time, beregnet ud fra timeserien og demand i noden i simuleringsåret (værdier i TVAR.csv er jo normerede)

PrepareHour(int hour):
Skal kunne give nogle kraftværker nedetid. Ikke implementeret i første omgang. 

GetProduction(int hour, string type):
Returnerer produktionen af denne energitype i area for den pågældende time. 

I senere implementationer af simuleringen skal denne klasse også håndtere nedetiden af værker. 



Line klassen holder styr på transmissionslinjer
Class: Line
__init__(string a, string b, double maxCapAB, double maxCapBA):
Konstruerer line-objekt.

GetMaxAB():
Returner maxcapaciteten fra A til B 

GetMaxBA():
Returner maxcapaciteten fra B til A

Denne klasse kan senere håndtere at en linje kan have et sammenbrud. 