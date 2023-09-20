from collections import defaultdict
from types import SimpleNamespace
from typing import Any, Dict, Generator, List, Tuple

from dyndesign.utils.misc import tuplefy
from .exposed_class_config import ClassConfig
from .dependency_configuration import DependencyConfiguration


class ClassConfigurationUnit:
    """
    The class embodying a class configuration unit, whose instances directly correspond to the positional arguments
    passed to the `@dynconfig` class decorator in a one-to-one fashion.
    """

    __LOCAL_CLASS_CONFIG_ATTRIBUTE = "DYNDESIGN_LOCAL_CONFIG"

    def __init__(self, class_config: Dict):
        """
        Initialize a class configuration unit.

        :param class_config: the user-defined configuration used to initialize the class configuration unit.
        """
        self.dependencies = defaultdict(list, self.__retrieve_dependencies(class_config))
        self.dependency_keys: List[str] = []
        self.local_config = self.dependencies.pop(self.__LOCAL_CLASS_CONFIG_ATTRIBUTE, SimpleNamespace()).__dict__

    @staticmethod
    def __get_dependency_item(config_item: Any) -> Any:
        """
        Convert the user-defined configurations of an item of user-defined configuration dictionary into
        corresponding in-place DependencyConfiguration instances.

        :param config_item: The item of user-defined configuration dictionary.
        :return: The converted configuration item.
        """
        if isinstance(config_item, tuple):
            return tuple(DependencyConfiguration(d) for d in config_item)
        elif isinstance(config_item, dict):
            return {k: DependencyConfiguration(v) for k, v in config_item.items()}
        elif isinstance(config_item, ClassConfig):
            return DependencyConfiguration(config_item)
        else:
            return config_item

    def __retrieve_dependencies(self, class_config: Dict) -> Dict:
        """
        Retrieve a class configuration dictionary where each ClassConfig instance from a user-defined configuration
        is used to initialize an in-place DependencyConfiguration instance.

        :param class_config: The user-defined configuration dictionary.
        :return: The class configuration dictionary.
        """
        return {key: self.__get_dependency_item(config_item) for key, config_item in class_config.items()}

    def __create_or_append_dependency_list(self, dep_key, dependency):
        """
        Create or append a new dependency with a given key.

        :param dep_key: The key of the dependency.
        :param dependency: The dependency to be created or appended to the dependencies with an existing key.
        """
        try:
            self.dependencies[dep_key].append(DependencyConfiguration(dependency))  # type: ignore
        except AttributeError:
            self.dependencies[dep_key] = [self.dependencies[dep_key], DependencyConfiguration(dependency)]

    def get_dependencies(self, dep_key: str) -> Generator[DependencyConfiguration, None, None]:
        """
        Get all canonical dependencies associated to a dependency key.

        :param dep_key: The dependency key to be queried.
        :return: The canonical dependencies associated to the key.
        """
        return (d for d in tuplefy(self.dependencies[dep_key]) if isinstance(d, DependencyConfiguration))

    def set_injection_method(self, dep_key: str, dependencies: Tuple[DependencyConfiguration, ...], method_name: str):
        """
        Set an injection method to the component dependencies passed from `@dynconfig` method decorators.

        :param dep_key: Key of the dependencies to be updated.
        :param dependencies: Dependencies to be updated.
        :param method_name: Name of the method to be injected.
        """
        for dependency in tuplefy(dependencies):
            if dependency.component_class:
                dependency.injection_method = method_name
                self.__create_or_append_dependency_list(dep_key, dependency)

    def populate_dependency_keys(self, option_order: Tuple[str, ...]):
        """
        Sort the option selectors based on the provided order, if any.

        :param option_order: The order to be used for sorting the option selectors.
        """
        if option_order:
            self.dependency_keys = sorted(
                self.dependencies.keys(),
                key=lambda i: option_order.index(i)
            )
        else:
            self.dependency_keys = list(self.dependencies.keys())
