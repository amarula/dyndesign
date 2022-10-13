import dyndee.dyn_methods as dynm
from .testing_results import DynamicMethodsResults as cdr


class A:

    @dynm.decorate_with("m2")
    def m1(self):
        return cdr.CLASS_A__M1

    def m2(self, func):
        return (func(self), cdr.CLASS_A__M2)


class B:

    @dynm.decorate_with("d1")
    def m1(self):
        return cdr.CLASS_B__M1


class C:

    def __init__(self, param1):
        self.param1 = param1

    def m1(self):
        with dynm.safezone("d2"):
            return self.d2()


class D:

    def m1(self):
        return dynm.invoke("d3", self)
