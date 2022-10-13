import dyndesign.dynmethod as dynm
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
            return self.d2()

    def m2(self):
        with dynm.safezone("d2"):
            self.does_not_exist()
            return self.d2()


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
