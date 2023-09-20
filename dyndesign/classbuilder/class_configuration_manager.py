from collections import defaultdict, namedtuple
from types import SimpleNamespace
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

from .class_importer import ClassImporter, TypeClassOrPath
from .dependency_configuration import DependencyConfiguration
from .class_configuration_unit import ClassConfigurationUnit
from dyndesign.utils.misc import class_to_dict, tuplefy

ClassConfigType = Union[Dict, TypeClassOrPath]
DependencyKeyType = Union[Callable, str]
MethodConfig = namedtuple("MethodConfig", ["method_name", "method_conf_unit"])


class ClassConfigurationManager:
    """A utility class for loading and processing class configuration options."""

    __SWITCH_KEY_SEPARATOR = "_#=_"

    SWITCH_DEFAULT = '_#!_SWITCH_DEFAULT'
    DEFAULT_UNIT_ID = 0

    def __init__(
            self,
            global_config: SimpleNamespace,
            class_configs: Tuple[ClassConfigType, ...],
            method_configs: Optional[List[MethodConfig]],
            assigned_class_configs: Dict
    ):
        """
        Initialize a ClassConfigurationManager instance.

        :param global_config: The global configuration.
        :param class_configs: The user-defined class configurations of the potential dependencies.
        :param method_configs: The configurations of potential components passed from method decorators.
        :param assigned_class_configs: The global configuration settings assigned using `set_configuration`.
        """
        self.__default_switches: Set = set()
        self.class_importer = ClassImporter(global_config)
        self.__assigned_class_configs = assigned_class_configs
        self.__init_class_configs(class_configs)
        self.global_conf = global_config
        self.__process_class_config(method_configs)

    def __get_class_config_unit(self, class_config: ClassConfigType) -> ClassConfigurationUnit:
        """
        Get the initialized class configuration unit for the potential dependency.

        :param class_config: The user-defined configuration for which to initialize class dependency configurations.
        :return: The initialized class configuration unit.
        """
        if not isinstance(class_config, dict):
            assigned_class_config = self.__assigned_class_configs.get(getattr(class_config, '__name__', None))
            class_config = class_to_dict(self.class_importer.get_imported_class(class_config))
            class_config.update(assigned_class_config or {})
        return ClassConfigurationUnit(class_config)

    def __init_class_configs(self, class_configs: Tuple[ClassConfigType, ...]):
        """
        Initialize the class dependency configurations for all the potential dependencies to be added using the
        user-defined class configurations.

        :param class_configs: The user-defined configurations of the potential dependencies.
        """
        self.class_configs = tuple(self.__get_class_config_unit(class_config) for class_config in class_configs)

    def __process_class_config(self, method_configs: Optional[List[MethodConfig]]):
        """
        Merge class and method configurations, then populate the class configuration keys.

        :param method_configs: The component configurations passed from method decorators.
        """
        for config_unit in self.class_configs:
            config_unit.dependencies = self.__transform_switches(config_unit.dependencies)
            if method_configs:
                self.__merge_method_configs(method_configs)
            config_unit.populate_dependency_keys(self.global_conf.option_order)

    @staticmethod
    def __is_switch_configuration(config_node: Any) -> bool:
        """
        Check if a config node represents a switch option configuration.

        :param config_node: The config node to check.
        :return: True if the node represents a switch option, False otherwise.
        """
        return isinstance(config_node, Dict) and not isinstance(config_node, DependencyConfiguration)

    def __transform_switches(self, class_config: defaultdict) -> defaultdict:
        """
        Transform each switch configuration into a set of boolean configurations, where each boolean configuration
        represents whether the corresponding option is selected or not.

        :param class_config: The dictionary of user-defined class configurations.
        :return: The transformed class configurations.
        """
        for dep_key, config_nodes in class_config.copy().items():
            for config_node in tuplefy(config_nodes):
                if self.__is_switch_configuration(config_node):
                    for option_key, config in config_node.items():
                        if option_key == self.SWITCH_DEFAULT:
                            self.__default_switches.add(dep_key)
                            class_config[dep_key] = config
                        else:
                            class_config[self.__get_switch_key(dep_key, option_key)] = config
                    if not isinstance(class_config[dep_key], DependencyConfiguration):
                        class_config.pop(dep_key)
        return class_config

    def __merge_method_configs(self, method_configs: List[MethodConfig]):
        """
        Merge the configurations passed from `@dynconfig` method decorators with the class configuration.

        :param method_configs: The component configurations passed from method decorators.
        """
        for method_config in method_configs:
            for dep_key, dependencies in self.__transform_switches(method_config.method_conf_unit).items():
                self.class_configs[self.DEFAULT_UNIT_ID].set_injection_method(dep_key, dependencies,
                                                                              method_config.method_name)

    def __get_switch_key(self, key: str, option: Any) -> str:
        """
        Generate a switch key from a couple of switch key/option.

        :param key: The original key.
        :param option: The switch option.
        :return: The generated switch key.
        """
        return self.__SWITCH_KEY_SEPARATOR.join((key, str(option)))

    def transform_options(self, options: Dict):
        """
        Transform a switch option into a set of boolean options, so that they are compatible with the corresponding
        transformed switch configurations.

        :param options: The configuration options to process.
        """
        switches_to_add = set()
        all_keys = tuple(dep_key for cc in self.class_configs for dep_key in cc.dependencies)
        for opt_key, option in options.copy().items():
            compound_key = self.__get_switch_key(opt_key, str(option))
            if compound_key in all_keys:
                options[compound_key] = True
                options.pop(opt_key)
                switches_to_add.add(opt_key)
        options.update((key, True) for key in self.__default_switches if key not in switches_to_add)

    def get_global_setting(self, dependency_config: DependencyConfiguration, key: str) -> Any:
        """
        Get a global setting for a class dependency configuration.

        :param dependency_config: The dependency configuration.
        :param key: The setting's key.
        :return: The global setting value.
        """
        return getattr(dependency_config, key, self.global_conf.__dict__[key])

    def get_default_global_config(self, dependency_config: Any, key: str) -> Any:
        """
        Get a default global setting for a class dependency configuration, if any.

        :param dependency_config: The dependency configuration.
        :param key: The setting's key.
        :return: The global setting value if any, None otherwise.
        """
        try:
            return getattr(dependency_config, key, None) or getattr(self.global_conf, key, None)
        except KeyError:
            return None

    def get_default_class(self, class_config: Any) -> Any:
        """
        Get the default dependent class from the class configuration, if any.

        :param class_config: The class configuration.
        :return: The default class if any, None otherwise.
        """
        return self.get_default_global_config(class_config, "default_class")

    def set_default_global_config(self, config_unit: ClassConfigurationUnit):
        """
        Set default non-empty values in a global configuration dictionary from the local configuration of a unit.

        :param config_unit: The configuration unit of the potential dependencies.
        """
        self.global_conf.__dict__.update((k, v) for k, v in config_unit.local_config.items() if v is not None)
