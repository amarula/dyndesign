from dyndesign import decoratewith, importclass, safeinvoke, safezone
from ..testing_results import DynamicMethodsResults as Cdr


class A:

    @decoratewith("m2")
    def m1(self):
        return Cdr.CLASS_A__M1

    def m2(self, func):
        return func(self), Cdr.CLASS_A__M2


class B:

    @decoratewith("d1")
    def m1(self):
        return Cdr.CLASS_B__M1


class C:

    def __init__(self, param1):
        self.param1 = param1

    def m1(self):
        with safezone():
            return self.d2()  # type: ignore

    def m2(self):
        with safezone("d2"):
            self.does_not_exist()  # type: ignore
            return self.d2()  # type: ignore


class D:

    def m1(self):
        return safeinvoke("d3", self)


class E:
    param1 = int

    def c1(self):
        self.param1 = Cdr.CLASS_E__C1

    @decoratewith("d4", fallback=c1)
    def m1(self):
        return Cdr.CLASS_E__M1


class F:
    param1 = int

    def c2(self):
        self.param1 = Cdr.CLASS_F__C2

    def m1(self):
        safeinvoke("d5", self, fallback=self.c2)
        return Cdr.CLASS_F__M1


class G:

    def d6(self, func):
        return func(self), Cdr.CLASS_DM_G__D6


class H(G):

    @decoratewith("d6")
    def m1(self):
        return Cdr.CLASS_H__M1


class I:

    def __init__(self):
        self.dm_i = importclass("tests.samples.sample_classes_imported.DmI")(Cdr.CLASS_I__A1)

    @decoratewith("dm_i.d7")
    def m1(self):
        return Cdr.CLASS_I__M1


class J:

    def __init__(self):
        self.dm_j = importclass("tests.samples.sample_classes_imported.DmJ")()

    @decoratewith("d8", "d9", method_sub_instance="dm_j")
    def m1(self):
        return Cdr.CLASS_J__M1


class K:

    def __init__(self, apply_decorator):
        self.apply_decorator = apply_decorator

    @decoratewith("d10", disable_property="apply_decorator")
    def m1(self):
        return Cdr.CLASS_K__M1


class L:

    def d10(self, func):
        return Cdr.CLASS_L__D10, func(self)
