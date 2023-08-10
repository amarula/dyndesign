from typing import Type

from dyndesign.dyninherit.dyninherit_base import DynInheritanceBase

__all__ = ["DynInheritance"]


class DynInheritance(DynInheritanceBase):
    """
    Enables classes to dynamically alter their set of parent classes using the 'DynInheritance' mechanism.

    Subclasses that inherit from the special class 'DynInheritance' gain the ability to dynamically adjust their
    superclass set. Instances of these classes are capable of automatically updating their superclass configuration in
    tandem with the class itself.

    Acknowledgements to @danilovmy for the inspiration behind this implementation.
    """

    def __init_subclass__(cls):
        """
        Initialize the subclass of 'DynInheritance' by configuring its dynamic inheritance attributes.
        """
        cls._dyn_class = DynInheritance
        super()._init_dyninherit_class()

    @classmethod
    def _dyn_inherit_from(cls, *parent_classes: Type, **_):
        """
        Replace the current superclass set of the dynamically inheriting class with a new set of classes.

        :param parent_classes: The new set of parent classes to be used as the superclass set.
        """
        cls.__bases__ = (*parent_classes,)
