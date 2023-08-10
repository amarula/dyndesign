from dyndesign import decoratewith
from ..testing_results import ClassResults as Cr


class A:
    def __init__(self):
        self.a1 = Cr.CLASS_A__A1
        self.a2 = Cr.CLASS_A__A2
        self.a3 = self.m1()

    @staticmethod
    def m1():
        return Cr.CLASS_A__M1

    @staticmethod
    def m2():
        return Cr.CLASS_A__M2


class B:
    def __init__(self):
        self.a1 = Cr.CLASS_B__A1
        self.a3 = self.m2()  # type: ignore

    def m1(self):
        return Cr.CLASS_B__M1


class BWithException:
    def __init__(self):
        # Raises a `TypeError` exception.
        self.a1 = Cr.CLASS_B__A1 + self.m2  # type: ignore


class BChild(B):
    def m1(self):
        return Cr.CLASS_B_CHILD__M1

    @staticmethod
    def m3():
        return Cr.CLASS_B_CHILD__M3


class C:
    def __init__(self):
        self.a3 = self.m3()  # type: ignore

    @staticmethod
    def m1():
        return Cr.CLASS_C__M1


class CChild(C):
    def __init__(self):
        super().__init__()
        self.a2 = Cr.CLASS_C_CHILD__A2

    @staticmethod
    def m2():
        return Cr.CLASS_C_CHILD__M2


class D:
    def __init__(self):
        self.m3 = self.m1  # type: ignore
        self.m2 = lambda: Cr.CLASS_D__M2


class E:
    def __init__(self, param_1, param_2):
        self.a1 = self.param_1 = param_1
        self.a2 = param_2

    def m2(self):
        return self.param_1


class F:
    def __init__(self, param_1):
        self.a2 = param_1

    @staticmethod
    def m2():
        return Cr.CLASS_F__M2


class G:
    def __init__(self, param_1, /, option=None, *, kwonly=None):
        self.a1 = option
        self.a2 = param_1
        self.a3 = kwonly


class H:
    def __init__(self, param_2, /, option_2=None, *, kwonly_2=None):
        self.a1 = option_2
        self.a2 = param_2
        self.a3 = kwonly_2

    @staticmethod
    def m2():
        return Cr.CLASS_H__M2


class I:
    @staticmethod
    def m1():
        return Cr.CLASS_I__M1


class J:
    a1: int

    def m1(self):
        self.a1 = Cr.CLASS_J__A1


class K:
    a2: int

    def m1(self):
        self.a2 = Cr.CLASS_K__A2


class L:
    a1: int

    def d1(self, func):
        self.a1 = Cr.CLASS_L__A1
        return func(self)

    def d2(self, func, param_1):
        param_1.append(Cr.CLASS_L__ITEM_1)
        func(self, param_1)
        param_1.append(Cr.CLASS_L__ITEM_2)
        return param_1


class M:
    a2: int

    def d1(self, func):
        self.a2 = Cr.CLASS_M__A2
        return func(self)

    def d2(self, func, param_1):
        param_1.append(Cr.CLASS_M__ITEM_1)
        func(self, param_1)
        param_1.append(Cr.CLASS_M__ITEM_2)
        return param_1


class N:
    def __init__(self):
        self.a3 = [Cr.CLASS_N__ITEM_1]

    @decoratewith("d1")
    def m1(self):
        self.a3 += [Cr.CLASS_N__ITEM_1]
        return self.a3


class O:
    @decoratewith("d2")
    def m1(self, param_1):
        param_1.append(Cr.CLASS_O__ITEM_2)
        return param_1

    def d2(self, func, param_1):
        param_1.append(Cr.CLASS_O__ITEM_1)
        func(self, param_1)
        param_1.append(Cr.CLASS_O__ITEM_3)
        return param_1


class P:
    @decoratewith("d2")
    def m1(self, param_1):
        param_1.append(Cr.CLASS_P__ITEM_1)
        return param_1

    def d2(self, func, param_1, param_2):
        param_1.append(param_2)
        func(self, param_1, param_2)
        return param_1
