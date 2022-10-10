from typing import Any, Callable, Tuple, Type
import inspect


class ClassInitMerger:
    """Merge a constructor of base class with the constructor(s) of the extension class(es)."""

    @staticmethod
    def __adapt_args(func: Callable, *args: Any) -> Tuple:
        """Return the first N input arguments based on the number of arguments accepted by an input function.

        :param func: input function.
        :param args: input arguments.
        :return: first N input arguments.
        """
        init_specs = inspect.getfullargspec(func)
        len_args = len(init_specs[0]) -1
        return args[:len_args]


    @classmethod
    def merge_class_inits(cls, classes: Tuple[Type, ...]) -> Callable:
        """Build an merged constructor by calling the constructors of the merged classes.

        :param classes: merged classes.
        :return: merged constructor.
        """
        class_constructors = []
        for cur_class in classes:
            if '__init__' in dir(cur_class):
                class_constructors.append(cur_class.__init__)

        def init_all_classes(obj, *args, **kwargs):
            for class_constructor in class_constructors:
                filtered_args = cls.__adapt_args(class_constructor, *args)
                class_constructor(obj, *filtered_args, **kwargs)

        return init_all_classes


class ClassMerger:
    """Merge a base class with one or more extension classes."""

    @staticmethod
    def merge(base_class: Type, *extension_classes: Type) -> Type:
        """Merge (i.e., extend) a base class with one or more extension classes. If more than one adapter classes are
        provided, then the classes are extended in sequence (from the first one to the last).

        :param base_class: base class.
        :param extension_classes: extension classes.
        :return: merged class.
        """
        result_classes = (base_class,) + extension_classes
        init_all_classes = ClassInitMerger.merge_class_inits(result_classes)
        return type(
            base_class.__name__,
            result_classes[::-1],
            {"__init__": init_all_classes}
        )
