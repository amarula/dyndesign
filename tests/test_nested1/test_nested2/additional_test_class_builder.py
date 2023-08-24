from ...testing_results import ClassResults as Cr


class A:
    def __init__(self):
        self.a1 = Cr.CLASS_A__A1
        self.a2 = Cr.CLASS_A__A2

    @staticmethod
    def m1():
        return Cr.CLASS_A__M1

    @staticmethod
    def m2():
        return Cr.CLASS_A__M2


class B:
    def __init__(self):
        self.a1 = Cr.CLASS_B__A1

    @staticmethod
    def m1():
        return Cr.CLASS_B__M1

    @staticmethod
    def m3():
        return Cr.CLASS_B__M3
