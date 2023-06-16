from ...samples.sample_classes_inheritance import *


class AdditionalDynIneritanceTests:

    @staticmethod
    def get_B_Locked():
        B_Locked.dynparents_add(A)
        return B_Locked
