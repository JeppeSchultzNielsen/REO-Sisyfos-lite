class Line:
    def __init__(self, a: str, b: str, maxCapAB: float, maxCapBA: float, name: str):
        self.a = a
        self.b = b
        self.maxCapAB = maxCapAB
        self.maxCapBA = maxCapBA
        self.name = name


    def PrepareHour(self, hour: int):
        pass

    def GetName(self):
        return self.name

    def GetA(self):
        return self.a

    def GetB(self):
        return self.b

    def GetMaxCapAB(self):
        return self.maxCapAB

    def GetMaxCapBA(self):
        return self.maxCapBA