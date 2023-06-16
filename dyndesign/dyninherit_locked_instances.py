from typing import Type, Optional
from types import ModuleType
import inspect
from pathlib import PosixPath
import sys

from dyndesign.dyninherit_base import DynInheritanceBase
from dyndesign.exceptions import ErrorClassNotFoundInModules
from dyndesign.utils import back_frame

__all__ = ["DynInheritanceLockedInstances"]


class DynInheritanceLockedInstances(DynInheritanceBase):
    """Classes that inherit from special class `DynInheritanceLockedInstances` are enabled to dynamically change their
    superclass set. The instances of the classes maintain locked superclasses while the classes they are instantiated
    from update their superclasses.
    """

    __MODULE_BACK_LEVEL = 5

    def __init_subclass__(cls):
        cls._dyn_class = DynInheritanceLockedInstances
        super()._init_dyninherit_class()


    @classmethod
    def __find_module(cls) -> ModuleType:
        """Find the module where the patching class is defined.

        :return: module of the class.
        """
        if cls.__module__ == '__main__':
            return sys.modules["__main__"]
        module_filename = back_frame(cls.__MODULE_BACK_LEVEL).f_code.co_filename
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
    def _dyn_inherit_from(cls, *parent_classes: Type, rename_to: Optional[str] = None):
        """Create a new class from the dynamically inheriting class with a given superclass set and make the new class
        available from the inheriting class's module.

        :param parent_classes: new set of superclasses.
        :param rename_to: name to which the dynamically inheriting class is optionally renamed.
        """
        child_module = cls.__find_module()
        new_class = type(cls.__name__, parent_classes, dict(cls.__dict__))
        if rename_to:
            child_name = new_class.__name__ = rename_to
        else:
            child_name = cls.__name__
        setattr(child_module, child_name, new_class)
