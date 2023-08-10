from typing import Type, Optional
from types import ModuleType
import inspect
from pathlib import PosixPath
import sys

from dyndesign.dyninherit.dyninherit_base import DynInheritanceBase
from dyndesign.exceptions import ErrorClassNotFoundInModules
from dyndesign.utils.inspector import back_frame, BackLevels

__all__ = ["DynInheritanceLockedInstances"]


class DynInheritanceLockedInstances(DynInheritanceBase):
    """
    Subclasses inheriting from the specialized class 'DynInheritanceLockedInstances' gain the ability to dynamically
    alter their superclass configuration. Instances of these classes maintain a fixed set of superclasses while their
    originating classes are capable of updating their superclass structure.
    """

    def __init_subclass__(cls):
        """
        Initialize the subclass of 'DynInheritanceLockedInstances' by configuring its dynamic inheritance attributes.
        """
        cls._dyn_class = DynInheritanceLockedInstances
        super()._init_dyninherit_class()

    @classmethod
    def __find_module(cls) -> ModuleType:
        """
        Locate the module in which the subclass is defined.

        :return: The module containing the class.
        """
        if cls.__module__ == '__main__':
            return sys.modules["__main__"]
        module_filename = back_frame(BackLevels.BACK_LEVEL_5).f_code.co_filename
        module_filename_stem = module_filename.rpartition('.')[0]
        module_parts = PosixPath(module_filename_stem).parts
        current_module_name = module_parts[-1]
        for part in module_parts[-2::-1]:
            if current_module := sys.modules.get(current_module_name):
                if inspect.isclass(getattr(current_module, cls.__name__, None)):
                    return current_module
            current_module_name = f"{part}.{current_module_name}"
        raise ErrorClassNotFoundInModules

    @classmethod
    def _dyn_inherit_from(cls, *parent_classes: Type, rename_to: Optional[str] = None, **kwargs):
        """
        Create a new class based on the dynamically inheriting class, with a given superclass configuration,
        and expose the new class within the originating class's module.

        :param parent_classes: The new set of parent classes to be used as the superclass configuration.
        :param rename_to: An optional name to assign to the newly created class.
        """
        child_module = cls.__find_module()
        new_class = type(cls.__name__, parent_classes, dict(cls.__dict__))
        if rename_to:
            child_name = new_class.__name__ = rename_to
        else:
            child_name = cls.__name__
        setattr(child_module, child_name, new_class)
