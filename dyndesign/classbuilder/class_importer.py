from types import SimpleNamespace
from typing import Type

from dyndesign.dynloader import importclass, TypeClassOrPath
from dyndesign.exceptions import DynConfigWrongClassType


class ClassImporter:
    """A utility class for importing classes based on provided paths or names."""

    def __init__(self, global_config: SimpleNamespace):
        """
        Initialize a ClassImporter instance.

        :param global_config: The global configuration options.
        """
        self.__global_config = global_config

    def get_imported_class(self, class_to_build: TypeClassOrPath) -> Type:
        """
        Get the imported class based on the provided class or path.

        :param class_to_build: The class or path to be imported.
        :return: The imported class.
        :raises WrongClassType: If the provided class type is invalid.
        """
        if isinstance(class_to_build, type):
            return class_to_build
        elif isinstance(class_to_build, str):
            # Handle importing classes based on paths or names
            if self.__global_config.class_builder_base_dir:
                class_to_build = '.'.join((self.__global_config.class_builder_base_dir, class_to_build))
            return importclass(class_to_build)
        else:
            raise DynConfigWrongClassType("Invalid class type provided.")
