from dyndesign import SingletonMeta


class A(metaclass=SingletonMeta):

    def __init__(self, param1=None):
        if param1:
            self.param1 = param1


class B(metaclass=SingletonMeta):

    def __init__(self, param1=None):
        if param1:
            self.param1 = param1
