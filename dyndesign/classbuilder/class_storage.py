from typing import Dict, Type


class ClassStorage:
    """A storage utility class for managing built classes."""
    config_map: Dict = {}
    classes_built: Dict = {}

    @classmethod
    def is_already_built(cls, class_to_build: Type) -> bool:
        """
        Check if a class is already built.

        :param class_to_build: The class to check.
        :return: True if the class is already built, False otherwise.
        """
        return class_to_build in cls.classes_built or class_to_build not in cls.config_map
