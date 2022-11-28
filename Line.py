class Line:
    def __init__(self, a: str, b: str, maxCapAB: float, maxCapBA: float):
        self.a = a
        self.b = b
        self.maxCapAB = maxCapAB
        self.maxCapBA = maxCapBA


    def PrepareHour(self, hour: int):
        pass

    def GetName(self):
        return self.a + "_to_" + self.b

    def GetA(self):
        return self.a

    def GetB(self):
        return self.b

    def GetMaxCapAB(self):
        return self.maxCapAB

    def GetMaxCapBA(self):
        return self.maxCapBA