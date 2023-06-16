from dyndesign import decoratewith, DynInheritance, DynInheritanceLockedInstances
from ..testing_results import ClassResults as cr


class A:
    def __init__(self):
        self.a1 = cr.CLASS_A__A1
        self.a2 = cr.CLASS_A__A2
        self.a3 = self.m1()

    def m1(self):
        return cr.CLASS_A__M1

    def m2(self):
        return cr.CLASS_A__M2


class B(DynInheritance):
    def __init__(self):
        super().__init__()
        self.a1 = cr.CLASS_B__A1

    def m1(self):
        return cr.CLASS_B__M1


class B_Locked(DynInheritanceLockedInstances):
    """B_Locked docstring"""
    def __init__(self):
        super(DynInheritanceLockedInstances, self).__init__()
        self.a1 = cr.CLASS_B__A1

    def m1(self):
        return cr.CLASS_B__M1


class C:
    def __init__(self):
        self.a1 = cr.CLASS_C__A1
        self.a3 = cr.CLASS_C__A3

    def m3(self):
        return cr.CLASS_C__M3


class D(DynInheritance, A):
    def __init__(self):
        super().__init__()
        self.safesuper(A, self).__init__()

    def m2(self):
        return cr.CLASS_D__M2


class D_Locked(DynInheritanceLockedInstances, A):
    def __init__(self):
        super(DynInheritanceLockedInstances, self).__init__()
        self.safesuper(A, self).__init__()

    def m2(self):
        return cr.CLASS_D__M2


class E:
    def __init__(self, param_1, param_2):
        self.a1 = self.param_1 = param_1
        self.a2 = param_2

    def m2(self):
        return self.param_1


class F_Locked(DynInheritanceLockedInstances):
    def __init__(self):
        self.a1 = cr.CLASS_F__A2
        super(DynInheritanceLockedInstances, self).__init__()

    def m2(self):
        return cr.CLASS_F__M2


class G(DynInheritance):
    def __init__(self):
        self.a1 = cr.CLASS_G__A1

    def m1(self):
        return self.safesuper(mocked_methods=("m1",)).m1() or cr.CLASS_G__M1  # type: ignore

    def self_add_A(self):
        self.dynparents_add(A)


class H:
    a1 = cr.CLASS_H__A1


class I(DynInheritance):
    def m1(self):
        return self.safesuper(mocked_attrs=("a1",)).a1 or cr.CLASS_I__M1  # type: ignore


class M:
    def d1(self, func):
        self.a2 += [cr.CLASS_M__ITEM_1] # type: ignore
        return func(self)


class N(DynInheritance):
    def __init__(self):
        self.a2 = []

    @decoratewith("d1")
    def m1(self):
        self.a2 += [cr.CLASS_N__ITEM_1]
        return self.a2
