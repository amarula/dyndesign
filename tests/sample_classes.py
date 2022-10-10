from .testing_results import ClassMergeResults as cmr


class A:
    def __init__(self):
        self.a1 = cmr.CLASS_A__A1
        self.a2 = cmr.CLASS_A__A2
        self.a3 = self.m1()

    def m1(self):
        return cmr.CLASS_A__M1

    def m2(self):
        return cmr.CLASS_A__M2


class B:
    def __init__(self):
        self.a1 = cmr.CLASS_B__A1
        self.a3 = self.m2()

    def m1(self):
        return cmr.CLASS_B__M1


class B_child(B):
    def m1(self):
        return cmr.CLASS_B_CHILD__M1

    def m3(self):
        return cmr.CLASS_B_CHILD__M3


class C:
    def __init__(self):
        self.a3 = self.m3()

    def m1(self):
        return cmr.CLASS_C__M1


class C_child(C):
    def __init__(self):
        super().__init__()
        self.a2 = cmr.CLASS_C_CHILD__A2

    def m2(self):
        return cmr.CLASS_C_CHILD__M2


class D:
    def __init__(self):
        self.m3 = self.m1
        self.m2 = lambda: cmr.CLASS_D__M2


class E:
    def __init__(self, param_1, param_2):
        self.a1 = self.param_1 = param_1
        self.a2 = param_2

    def m2(self):
        return self.param_1


class F:
    def __init__(self, param_1):
        self.a2 = param_1

    def m2(self):
        return cmr.CLASS_F__M2
