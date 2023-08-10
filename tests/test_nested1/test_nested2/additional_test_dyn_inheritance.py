from ...samples.sample_classes_inheritance import *


class AdditionalDynInheritanceTests:

    @staticmethod
    def get_BLocked():
        BLocked.dynparents_add(A)
        return BLocked
