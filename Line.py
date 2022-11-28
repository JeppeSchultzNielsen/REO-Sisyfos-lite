class Line:
    def __init__(self, a: str, b: str, maxCapAB: float, maxCapBA: float):
        self.a = a
        self.b = b

    def PrepareHour(self, hour: int):
        pass

    def GetName(self):
        return self.a + "_to_" + self.b
    #Test om jeg kan push