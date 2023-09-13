from typing import Any, Tuple

from dyndesign.exceptions import NoMethodFound


def tuplefy(item: Any) -> Tuple:
    """
    Convert an item to a tuple if it is not already a tuple.

    :param item: The item to be converted.
    :return: A tuple containing the item or the item itself if it is already a tuple.
    """
    if isinstance(item, tuple):
        return item
    elif isinstance(item, list):
        return tuple(item)
    else:
        return (item,)


def get_dot_basename(dotted_name: str) -> str:
    """
    Get the base name of a name in dot notation.

    :param dotted_name: The name in dot notation.
    :return: The base name.
    """
    return dotted_name.rsplit('.', 1)[0]


def class_to_dict(obj: object) -> dict:
    """
    Convert a class object to a dictionary of non-private attributes.

    :param obj: The object to be converted.
    :return: A dictionary containing non-private attributes and their values.
    """
    class_dict = {}
    for key, value in vars(obj).items():
        if not key.startswith('__'):
            class_dict[key] = value
    return class_dict


def invoke_first_method(obj: object, method_names: Tuple[str, ...], *args, **kwargs) -> Any:
    """
    Attempt to invoke a method from a tuple of method names on an object. The first method that is found is invoked and
    its result is returned. If no method is found, an exception is raised.

    :param obj: The object on which to invoke the methods.
    :param method_names: The method names to try.
    :param args: Positional arguments to be passed to each method.
    :param kwargs: Keyword arguments to be passed to each method.
    :return: The value returned by the first method found, if any.
    """
    for method_name in method_names:
        if method := getattr(obj, method_name, None):
            return method(*args, **kwargs)
    raise NoMethodFound
