from dyndesign import DynInheritance, DynInheritanceLockedInstances
from ..testing_results import ClassResults as Cr, DynamicMethodsResults as Cdr


class A:
    def __init__(self):
        self.a1 = Cr.CLASS_A__A1

    @staticmethod
    def m1():
        return Cr.CLASS_A__M1


class B:
    def __init__(self):
        self.a1 = Cr.CLASS_B__A1

    @staticmethod
    def m1():
        return Cr.CLASS_B__M1


class C:
    pass


class DmB:

    def d1(self, func):
        return func(self), Cdr.CLASS_DM_B__D1


class DmC:

    def d2(self):
        return self.param1, Cdr.CLASS_DM_C__D2  # type: ignore


class DmD:

    @staticmethod
    def d3():
        return Cdr.CLASS_DM_D__D3


class DmI:

    def __init__(self, param1):
        self.a1 = param1

    def d7(self, func, decorated_self):
        return func(decorated_self), self.a1


class DmJ:

    @staticmethod
    def d8(func, decorated_self):
        return Cdr.CLASS_DM_J__D8, *func(decorated_self)

    @staticmethod
    def d9(func, decorated_self):
        return Cdr.CLASS_DM_J__D9, func(decorated_self)


class E(DynInheritance):
    def __init__(self):
        self.a1 = Cr.CLASS_E__A2
        super().__init__()

    @staticmethod
    def m2():
        return Cr.CLASS_E__M2


class ELocked(DynInheritanceLockedInstances):
    def __init__(self):
        self.a1 = Cr.CLASS_F__A2
        super().__init__()

    @staticmethod
    def m2():
        return Cr.CLASS_F__M2
