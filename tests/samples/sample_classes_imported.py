from dyndesign import DynInheritance, DynInheritanceLockedInstances
from ..testing_results import ClassResults as cr, DynamicMethodsResults as cdr


class A:
    def __init__(self):
        self.a1 = cr.CLASS_A__A1

    def m1(self):
        return cr.CLASS_A__M1


class B:
    def __init__(self):
        self.a1 = cr.CLASS_B__A1

    def m1(self):
        return cr.CLASS_B__M1


class C:
    pass


class DM_B:

    def d1(self, func):
        return (func(self), cdr.CLASS_DM_B__D1)


class DM_C:

    def d2(self):
        return (self.param1, cdr.CLASS_DM_C__D2)  # type: ignore


class DM_D:

    def d3(self):
        return cdr.CLASS_DM_D__D3


class DM_I:

    def __init__(self, param1):
        self.a1 = param1

    def d7(self, func, decorated_self):
        return (func(decorated_self), self.a1)


class DM_J:

    def d8(self, func, decorated_self):
        return (cdr.CLASS_DM_J__D8, *func(decorated_self))

    def d9(self, func, decorated_self):
        return (cdr.CLASS_DM_J__D9, func(decorated_self))


class E(DynInheritance):
    def __init__(self):
        self.a1 = cr.CLASS_E__A2
        super().__init__()

    def m2(self):
        return cr.CLASS_E__M2


class E_Locked(DynInheritanceLockedInstances):
    def __init__(self):
        self.a1 = cr.CLASS_F__A2
        super().__init__()

    def m2(self):
        return cr.CLASS_F__M2
