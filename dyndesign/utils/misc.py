from typing import Any, Tuple


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
