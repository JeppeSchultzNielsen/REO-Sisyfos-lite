#options class keeps track of all options 

class Options:
    def __init__(self):
        self.usePlannedDownTime = True
        self.useUnplannedDownTime = True
        self.userSetFlexDems = False
        self.demFlexKlassisk = 0
        self.demFlexCVP = 0.9
        self.demFlexPtX = 1
        self.demFlexTransport = 0.1
        self.storebaelt2 = False
        self.oresundOpen = False
        self.energyIslandEast = False
        self.energyIslandWest = False 
        self.useVariations = False #Use variations when making the outageplan. Only relevant when creating a new outageplan. 

    def setFlex(self, klassisk, cvp, ptx, transport):
        self.userSetFlexDems = True
        self.demFlexKlassisk = klassisk
        self.demFlexCVP = cvp
        self.demFlexPtX = ptx
        self.demFlexTransport = transport 
    
