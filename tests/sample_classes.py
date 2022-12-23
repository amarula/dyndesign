from dyndesign import decoratewith
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
        self.a3 = self.m2()  # type: ignore

    def m1(self):
        return cmr.CLASS_B__M1


class B_child(B):
    def m1(self):
        return cmr.CLASS_B_CHILD__M1

    def m3(self):
        return cmr.CLASS_B_CHILD__M3


class C:
    def __init__(self):
        self.a3 = self.m3()  # type: ignore

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
        self.m3 = self.m1  # type: ignore
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

    def m2(self):
        return cmr.CLASS_H__M2


class I:
    def m1(self):
        return cmr.CLASS_I__M1


class J:
    def m1(self):
        self.a1 = cmr.CLASS_J__A1


class K:
    def m1(self):
        self.a2 = cmr.CLASS_K__A2


class L:
    def d1(self, func):
        self.a1 = cmr.CLASS_L__A1
        return func(self)

    def d2(self, func, param_1):
        param_1.append(cmr.CLASS_L__ITEM_1)
        func(self, param_1)
        param_1.append(cmr.CLASS_L__ITEM_2)
        return param_1


class M:
    def d1(self, func):
        self.a2 = cmr.CLASS_M__A2
        return func(self)

    def d2(self, func, param_1):
        param_1.append(cmr.CLASS_M__ITEM_1)
        func(self, param_1)
        param_1.append(cmr.CLASS_M__ITEM_2)
        return param_1


class N:
    def __init__(self):
        self.a3 = [cmr.CLASS_N__ITEM_1]

    @decoratewith("d1")
    def m1(self):
        self.a3 += [cmr.CLASS_N__ITEM_1]
        return self.a3


class O:
    @decoratewith("d2")
    def m1(self, param_1):
        param_1.append(cmr.CLASS_O__ITEM_2)
        return param_1

    def d2(self, func, param_1):
        param_1.append(cmr.CLASS_O__ITEM_1)
        func(self, param_1)
        param_1.append(cmr.CLASS_O__ITEM_3)
        return param_1


class P:
    @decoratewith("d2")
    def m1(self, param_1):
        param_1.append(cmr.CLASS_P__ITEM_1)
        return param_1

    def d2(self, func, param_1, param_2):
        param_1.append(param_2)
        func(self, param_1, param_2)
        return param_1
