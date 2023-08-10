from typing import Any, Callable, Type, Union

__all__ = ["importclass", "preprocess_classes", "TypeClassOrPath"]

TypeClassOrPath = Union[Type, str]


def importclass(
    module_name: str,
    class_name: Union[str, None] = None
) -> Type:
    """
    Dynamically import a class from a specified module.

    :param module_name: The name of the module to import.
    :param class_name: The name of the class in the module to import. Defaults to None.
    :return: The dynamically imported class.
    """
    if not class_name:
        module_name, class_name = module_name.rsplit('.', 1)
    loaded_module = __import__(module_name, fromlist=[class_name])
    return getattr(loaded_module, class_name)


def preprocess_classes(func: Callable) -> Callable:
    """Decorator to convert dot-notated class paths into strings from positional arguments."""
    def __preprocess_classes_wrapper(*all_classes: TypeClassOrPath, **kwargs: Any) -> Any:
        """
        Dynamically import classes if they are passed as strings.

        :param all_classes: A variable number of class paths (strings or actual types).
        :param kwargs: Any keyword arguments to pass to the decorated function.
        :return: The result of the decorated function.
        """
        classes_processed = (
            class_id if isinstance(class_id, type)
            else importclass(class_id)
            for class_id in all_classes
        )
        return func(*classes_processed, **kwargs)
    return __preprocess_classes_wrapper
