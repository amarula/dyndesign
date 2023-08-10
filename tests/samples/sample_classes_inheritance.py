from dyndesign import decoratewith, DynInheritance, DynInheritanceLockedInstances
from ..testing_results import ClassResults as Cr


class A:
    def __init__(self):
        self.a1 = Cr.CLASS_A__A1
        self.a2 = Cr.CLASS_A__A2
        self.a3 = self.m1()

    @staticmethod
    def m1():
        return Cr.CLASS_A__M1

    def m2(self):
        return Cr.CLASS_A__M2


class B(DynInheritance):
    def __init__(self):
        super().__init__()
        self.a1 = Cr.CLASS_B__A1

    @staticmethod
    def m1():
        return Cr.CLASS_B__M1


class BLocked(DynInheritanceLockedInstances):
    """BLocked docstring"""
    def __init__(self):
        super(DynInheritanceLockedInstances, self).__init__()
        self.a1 = Cr.CLASS_B__A1

    @staticmethod
    def m1():
        return Cr.CLASS_B__M1


class C:
    def __init__(self):
        self.a1 = Cr.CLASS_C__A1
        self.a3 = Cr.CLASS_C__A3

    @staticmethod
    def m3():
        return Cr.CLASS_C__M3


class D(DynInheritance, A):
    def __init__(self):
        super().__init__()
        self.safesuper(A, self).__init__()

    def m2(self):
        return Cr.CLASS_D__M2


class DLocked(DynInheritanceLockedInstances, A):
    def __init__(self):
        super(DynInheritanceLockedInstances, self).__init__()
        self.safesuper(A, self).__init__()

    def m2(self):
        return Cr.CLASS_D__M2


class E:
    def __init__(self, param_1, param_2):
        self.a1 = self.param_1 = param_1
        self.a2 = param_2

    def m2(self):
        return self.param_1


class FLocked(DynInheritanceLockedInstances):
    def __init__(self):
        self.a1 = Cr.CLASS_F__A2
        super(DynInheritanceLockedInstances, self).__init__()

    @staticmethod
    def m2():
        return Cr.CLASS_F__M2


class G(DynInheritance):
    def __init__(self):
        self.a1 = Cr.CLASS_G__A1

    def m1(self):
        return self.safesuper(mocked_methods=("m1",)).m1() or Cr.CLASS_G__M1  # type: ignore

    def self_add_A(self):
        self.dynparents_add(A)


class H:
    a1 = Cr.CLASS_H__A1


class I(DynInheritance):
    def m1(self):
        return self.safesuper(mocked_attrs=("a1",)).a1 or Cr.CLASS_I__M1  # type: ignore


class M:
    def d1(self, func):
        self.a2 += [Cr.CLASS_M__ITEM_1]  # type: ignore
        return func(self)


class N(DynInheritance):
    def __init__(self):
        self.a2 = []

    @decoratewith("d1")
    def m1(self):
        self.a2 += [Cr.CLASS_N__ITEM_1]
        return self.a2
