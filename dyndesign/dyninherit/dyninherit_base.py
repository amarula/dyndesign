from typing import Type, Tuple, Union
import abc
from builtins import super as builtin_super

from dyndesign.dynloader import preprocess_classes
from dyndesign.utils.inspector import back_frame, BackLevels

__all__ = ["DynInheritanceBase", "safesuper"]

TypeObjectSuper = Union[object, super, None]
TypeTupleOptEmpty = Union[Tuple[str, ], Tuple[()]]


class DynInheritanceBase:
    """Base class for enabling dynamic inheritance of classes."""

    _dyn_class = object
    _initial_bases = ()

    @classmethod
    @abc.abstractmethod
    def _dyn_inherit_from(cls, *parent_classes: Type, **kwargs):
        """Abstract method to update the superclass set of a class."""
        raise NotImplementedError

    @classmethod
    def _init_dyninherit_class(cls):
        """Store the initial superclass set of a class."""
        if not cls._initial_bases:
            cls._initial_bases = cls.__bases__

    @classmethod
    def __filter_superclasses_out(cls, *classes_to_remove: Type) -> Tuple[Type, ...]:
        """
        Filter out specified classes from the superclass set of the class to be patched.

        :param classes_to_remove: Classes to be removed from the superclass set.
        :return: Classes in the superclass set that are not in `classes_to_remove`.
        """
        return tuple(set(cls.__bases__) - set(classes_to_remove))

    @classmethod
    def __super_overridden(cls) -> super:
        """
        Override the `super` function with no arguments to ensure correct behavior in instances of patched classes.

        :return: Super proxy object for the class instance.
        """
        self = back_frame(BackLevels.BACK_LEVEL_3).f_locals["self"]
        return builtin_super(self.__class__.__base__, self)

    @classmethod
    def dynparents_get(cls) -> Tuple[Type, ...]:
        """
        Get the superclass set of the dynamically inheriting class, excluding the special classes.

        :return: Superclasses of the class.
        """
        return cls.__filter_superclasses_out(object, cls._dyn_class)

    @classmethod
    @preprocess_classes
    def dynparents_add(cls, *parent_classes: Type, **kwargs):
        """
        Add the given classes to the superclass set of the dynamically inheriting class.

        :param parent_classes: Parent classes or paths to classes to be added to the superclass set.
        """
        parent_classes = cls.__bases__ + parent_classes
        cls._dyn_inherit_from(*parent_classes, **kwargs)

    @classmethod
    @preprocess_classes
    def dynparents_remove(cls, *classes_to_remove: Type, **kwargs):
        """
        Remove the given classes from the superclass set of the dynamically inheriting class.

        :param classes_to_remove: Parent classes or paths to classes to be removed from the superclass set.
        """
        if cls._dyn_class in classes_to_remove:
            classes_to_remove = tuple(filter(lambda c: c != cls._dyn_class, classes_to_remove))
        parent_classes = cls.__filter_superclasses_out(*classes_to_remove)
        cls._dyn_inherit_from(*parent_classes, **kwargs)

    @classmethod
    @preprocess_classes
    def dynparents_replace(cls, *parent_classes: Type, **kwargs):
        """
        Replace the superclass set of the dynamically inheriting class with the given classes.

        :param parent_classes: Parent classes or paths to classes to be used as the new superclass set.
        """
        parent_classes = (cls._dyn_class,) + parent_classes
        cls._dyn_inherit_from(*parent_classes, **kwargs)

    @classmethod
    @preprocess_classes
    def dynparents_restore(cls):
        """Restore the initial superclass set of the dynamically inheriting class."""
        cls._dyn_inherit_from(*cls._initial_bases)

    @classmethod
    def safesuper(
        cls,
        subclass: Type = None,
        object_or_type: TypeObjectSuper = None,
        mocked_attrs: TypeTupleOptEmpty = (),
        mocked_methods: TypeTupleOptEmpty = ()
    ) -> TypeObjectSuper:
        """
        A safe version of the `super` function to access superclasses safely.

        This prevents a `TypeError` exception when requested superclasses are not included
        in the superclass set of the dynamically inheriting class.

        :param subclass: The class passed as first argument to the `super` function.
        :param object_or_type: The object or class for the `super` function.
        :param mocked_attrs: Attribute names to mock if missing in the superclasses.
        :param mocked_methods: Method names to mock if missing in the superclasses.
        :return: A `super` proxy object if requested superclasses are included, or an object mocked with
                 `mocked_attrs`/`mocked_methods` if those attributes/methods are missing, or None.
        """
        try:
            if not subclass or not object_or_type:
                super_obj = cls.__super_overridden()
            else:
                super_obj = builtin_super(subclass, object_or_type)
            if mocked_methods or mocked_attrs:
                for class_property in mocked_methods + mocked_attrs:
                    if not hasattr(super_obj, class_property):
                        raise TypeError
            return super_obj
        except TypeError:
            if mocked_methods or mocked_attrs:
                class ClassMock:
                    def __getattr__(self, attr):
                        if attr not in self.__dict__:
                            if attr in mocked_methods:
                                return lambda *_, **__: None
                            elif attr in mocked_attrs:
                                return None
                        return getattr(self.obj, attr)

                return ClassMock()
            else:
                return None


def safesuper(
    subclass: Type,
    object_or_type: TypeObjectSuper,
    mocked_attrs: TypeTupleOptEmpty = (),
    mocked_methods: TypeTupleOptEmpty = ()
) -> TypeObjectSuper:
    """
    A function to invoke `DynInheritanceBase.safesuper`.

    This function can be used within the context of dynamically inherited classes or as a standalone function
    requiring mandatory `type` and `object_or_type` arguments.
    """
    return DynInheritanceBase.safesuper(subclass, object_or_type, mocked_attrs, mocked_methods)
