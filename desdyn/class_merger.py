from typing import Callable, List, Tuple, Type


class ClassMerger:
    """Merge a base class with one or more extension classes."""

    @staticmethod
    def __merge_class_inits(classes: Tuple[Type, ...]) -> Callable:
        """Build an merged constructor by calling the constructors of the merged classes.

        :param classes: merged classes.
        :return: merged constructor.
        """
        class_constructors = []
        for cur_class in classes:
            if '__init__' in dir(cur_class):
                class_constructors.append(cur_class.__init__)

        def init_all_classes(self, *args, **kwargs):
            for class_constructor in class_constructors:
                # Constructors of merged classes can either accept arguments or not. The first hypothesis is tried
                # first, if the number of arguments does not match then the second one is tried.
                try:
                    class_constructor(self, *args, **kwargs)
                except TypeError:
                    class_constructor(self)

        return init_all_classes


    @classmethod
    def merge_classes(cls, base_class: Type, extension_classes: List[Type]) -> Type:
        """Merge (i.e., extend) a base class with one or more extension classes. If more than one adapter classes are
        provided, then the classes are extended in sequence (from the first one to the last).

        :param base_class: base class.
        :param extension_classes: extension classes.
        :return: merged class.
        """
        result_classes = tuple(extension_classes + [base_class])
        init_all_classes = cls.__merge_class_inits(result_classes)
        return type(
            base_class.__name__,
            result_classes,
            {"__init__": init_all_classes}
        )
