from .testing_results import ClassMergeResults as cmr, DynamicMethodsResults as cdr


class A:
    def __init__(self):
        self.a1 = cmr.CLASS_A__A1

    def m1(self):
        return cmr.CLASS_A__M1


class B:
    def __init__(self):
        self.a1 = cmr.CLASS_B__A1

    def m1(self):
        return cmr.CLASS_B__M1


class C:
    pass


class DM_B:

    def d1(self, func):
        return (func(self), cdr.CLASS_DM_B__D1)


class DM_C:

    def d2(self):
        return (self.param1, cdr.CLASS_DM_C__M1)


class DM_D:

    def d3(self):
        return cdr.CLASS_DM_D__M1
