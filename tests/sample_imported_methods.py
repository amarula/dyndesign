import dyndesign.dynmethod as dynm
from dyndesign.dynloader import importclass
from .testing_results import DynamicMethodsResults as cdr


class A:

    @dynm.decoratewith("m2")
    def m1(self):
        return cdr.CLASS_A__M1

    def m2(self, func):
        return (func(self), cdr.CLASS_A__M2)


class B:

    @dynm.decoratewith("d1")
    def m1(self):
        return cdr.CLASS_B__M1


class C:

    def __init__(self, param1):
        self.param1 = param1

    def m1(self):
        with dynm.safezone():
            return self.d2()  # type: ignore

    def m2(self):
        with dynm.safezone("d2"):
            self.does_not_exist()  # type: ignore
            return self.d2()  # type: ignore


class D:

    def m1(self):
        return dynm.invoke("d3", self)


class E:

    def c1(self):
        self.param1 = cdr.CLASS_E__C1

    @dynm.decoratewith("d4", decorator_fallback=c1)
    def m1(self):
        return cdr.CLASS_E__M1


class F:

    def c2(self):
        self.param1 = cdr.CLASS_F__C2

    def m1(self):
        dynm.invoke("d5", self, method_fallback=self.c2)
        return cdr.CLASS_F__M1


class G:

    def d6(self, func):
        return (func(self), cdr.CLASS_DM_G__D6)


class H(G):

    @dynm.decoratewith("d6")
    def m1(self):
        return cdr.CLASS_H__M1


class I:

    def __init__(self):
        self.dm_i = importclass("tests.sample_classes_imported.DM_I")(cdr.CLASS_I__A1)

    @dynm.decoratewith("dm_i.d7")
    def m1(self):
        return cdr.CLASS_I__M1


class J:

    def __init__(self):
        self.dm_j = importclass("tests.sample_classes_imported.DM_J")()

    @dynm.decoratewith("d8", "d9", method_sub_instance="dm_j")
    def m1(self):
        return cdr.CLASS_J__M1
