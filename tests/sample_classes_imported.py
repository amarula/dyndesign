from .testing_results import ClassMergeResults as cmr


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
