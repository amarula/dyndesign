from typing import Type, Tuple, Union
import abc
from builtins import super as builtin_super

from dyndesign.dynloader import preprocess_classes
from dyndesign.utils import back_frame

__all__ = ["DynInheritanceBase", "safesuper"]

TypeObjectSuper = Union[object, super, None]
TypeTupleOptEmpty = Union[Tuple[str, ], Tuple[()]]


class DynInheritanceBase:
    """Base class for the special classes enabling classes to dynamic inheritance."""

    __SUPER_OVERRIDEN_BACK_LEVEL = 3

    _dyn_class = object
    _initial_bases = ()


    @classmethod
    @abc.abstractmethod
    def _dyn_inherit_from(cls, *parent_classes: Type):
        """Abstract method implementing the update of superclass set of a class."""
        raise NotImplementedError


    @classmethod
    def _init_dyninherit_class(cls):
        """Perform setup operations each time that a class inherits from `DynInheritanceBase`'s subclasses."""
        if not cls._initial_bases:
            cls._initial_bases = cls.__bases__


    @classmethod
    def __filter_superclasses_out(cls, *classes_to_remove: Type) -> Tuple[Type, ...]:
        """Filter the classes passed out of the superclass set of the class to be patched.

        :param classes_to_remove: classes to filter out of the superclass set.
        :return: classes in superclass set that are not in `classes_to_remove`.
        """
        return tuple(set(cls.__bases__) - set(classes_to_remove))


    @classmethod
    def __super_overriden(cls) -> super:
        """Method overriding `super` function with no arguments to make it correctly work in instances of patched
        class.

        :return: super proxy object for the class instance.
        """
        self = back_frame(cls.__SUPER_OVERRIDEN_BACK_LEVEL).f_locals["self"]
        return builtin_super(self.__class__.__base__, self)


    @classmethod
    def dynparents_get(cls) -> Tuple[Type, ...]:
        """Get the superclass set of the dynamically inheriting class, excluding the special classes.

        :return: superclasses of the class."""
        return cls.__filter_superclasses_out(object, cls._dyn_class)


    @classmethod
    @preprocess_classes
    def dynparents_add(cls, *parent_classes: Type, **kwargs):
        """Add the given classes to the superclass set of the dynamically inheriting class.

        :param parent_classes: parent classes or path-to-classes to add to the superclass set.
        """
        parent_classes = cls.__bases__ + parent_classes
        cls._dyn_inherit_from(*parent_classes, **kwargs)


    @classmethod
    @preprocess_classes
    def dynparents_remove(cls, *classes_to_remove: Type, **kwargs):
        """Remove the given classes from the superclass set of the dynamically inheriting class.

        :param parent_classes: parent classes or path-to-classes to remove from the superclass set.
        """
        if cls._dyn_class in classes_to_remove:
            classes_to_remove = tuple(filter(lambda c: c != cls._dyn_class, classes_to_remove))
        parent_classes = cls.__filter_superclasses_out(*classes_to_remove)
        cls._dyn_inherit_from(*parent_classes, **kwargs)


    @classmethod
    @preprocess_classes
    def dynparents_replace(cls, *parent_classes: Type, **kwargs):
        """Replace the superclass set of the dynamically inheriting class with the given classes.

        :param parent_classes: parent classes or path-to-classes to be used as superclass set.
        """
        parent_classes = (cls._dyn_class,) + parent_classes
        cls._dyn_inherit_from(*parent_classes, **kwargs)


    @classmethod
    @preprocess_classes
    def dynparents_restore(cls):
        """Restore the initial superclass set of the dynamically inheriting class."""
        cls._dyn_inherit_from(*cls._initial_bases)


    @classmethod
    def safesuper(cls,
        type: Type = None,
        object_or_type: TypeObjectSuper = None,
        mocked_attrs: TypeTupleOptEmpty = (),
        mocked_methods: TypeTupleOptEmpty = ()
    ) -> TypeObjectSuper:
        """As exception-safe version of the `super` function, `safesuper` can be utilized to safely access
        superclasses, preventing a `TypeError` exception in cases where those requested superclasses are not included
        in the superclass set of the dynamically inheriting class.

        :param type: class passed as first argument to `super`.
        :param object_or_type: object or class passed as second argument to `super`.
        :param mocked_attrs: attribute names that are mocked in case that the corresponding attributes are missing in
                             the superclasses.
        :param mocked_methods: method names that are mocked in case that the corresponding methods are missing in the
                               superclasses.
        :return: a `super` proxy object if the requested superclasses are included in the superclass set, otherwise an
                 object mocked with the `mocked_attrs`/`mocked_methods` if those attributes/methods are missing in the
                 superclass set, otherwise None.
        """
        try:
            if not type or not object_or_type:
                super_obj = cls.__super_overriden()
            else:
                super_obj = builtin_super(type, object_or_type)
            if mocked_methods or mocked_attrs:
                for property in mocked_methods + mocked_attrs:
                    if not hasattr(super_obj, property):
                        raise TypeError
            return super_obj
        except(TypeError):
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
        type: Type,
        object_or_type: TypeObjectSuper,
        mocked_attrs: TypeTupleOptEmpty = (),
        mocked_methods: TypeTupleOptEmpty = ()
    ) -> TypeObjectSuper:
    """Intermediate invoker function to call `DynInheritanceBase.safesuper`. This applies not only within the context of
    a dynamically inherited class, but also as a standalone function, requiring mandatory `type` and `object_or_type`
    arguments.
    """
    return DynInheritanceBase.safesuper(type, object_or_type, mocked_attrs, mocked_methods)
