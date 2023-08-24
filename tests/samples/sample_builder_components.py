from ..testing_results import ClassResults as Cr


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


class C:
    def __init__(self):
        self.a3 = Cr.CLASS_C__A3

    @staticmethod
    def m2():
        return Cr.CLASS_C__M2

    @staticmethod
    def m3():
        return Cr.CLASS_C__M3


class G:
    def __init__(self, param_1, /, optional=None, *, kwonly=None):
        self.param_1 = param_1
        self.optional = optional
        self.kwonly = kwonly


class H:
    def __init__(self, param_1, param_2, /, optional_2=None, *, kwonly_2=None):
        self.param_1 = param_1
        self.param_2 = param_2
        self.optional_2 = optional_2
        self.kwonly_2 = kwonly_2
