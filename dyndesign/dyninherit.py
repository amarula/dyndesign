from typing import Type

from dyndesign.dyninherit_base import DynInheritanceBase

__all__ = ["DynInheritance"]


class DynInheritance(DynInheritanceBase):
    """Classes that inherit from special class `DynInheritance` are enabled to dynamically change their superclass set.
    The instances of the classes live-update their superclasses along with the classes they are instantiated from.
    Thanks to @danilovmy for the inspiration.
    """

    def __init_subclass__(cls):
        cls._dyn_class = DynInheritance
        super()._init_dyninherit_class()


    @classmethod
    def _dyn_inherit_from(cls, *parent_classes: Type, **_):
        """Replace the superclass set of the dynamically inheriting class with a new set of classes.

        :param parent_classes: new set of superclasses.
        """
        cls.__bases__ = (*parent_classes,)
