from typing import Any, Callable, Type


class ParentClassBuilder:
    """ParentClassBuilder manages the addition of parent classes to a base class."""

    def __init__(self, base_class: Type, configure_dependent_class_callback: Callable):
        """
        Initialize the ParentClassBuilder instance.

        :param base_class: The base class upon which to build the new class.
        :param configure_dependent_class_callback: A callback invoked to recursively configure the parent classes.
        """
        self.__parent_classes = [base_class]
        self.parent_classes_configured = ()
        self.__configure_dependent_class = configure_dependent_class_callback
        if base_class.__bases__ != (object,):
            self.__parent_classes += base_class.__bases__

    def select_parent_classes(self, parent_classes: Any):
        """
        Add parent classes to the list of selected base classes to be used in the built class.

        :param parent_classes: The parent class or tuple of parent classes to add.
        """
        if isinstance(parent_classes, tuple):
            self.__parent_classes += list(parent_classes)
        else:
            self.__parent_classes.append(parent_classes)

    def configure_parent_classes(self):
        """
        Recursively configure all the parent classes of the built class, whether they are statically defined or
        dynamically added.
        """
        self.parent_classes_configured = tuple(self.__configure_dependent_class(pc) for pc in self.__parent_classes)
