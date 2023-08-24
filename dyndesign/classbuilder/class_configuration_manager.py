from collections import defaultdict
from types import SimpleNamespace
from typing import Any, Dict, List, Optional, Set, Type, Union

from .class_importer import ClassImporter, TypeClassOrPath
from .class_builder_config import ClassConfig
from dyndesign.utils.misc import class_to_dict, tuplefy

ClassConfigType = Union[Dict, TypeClassOrPath]


class ClassConfigurationManager:
    """A utility class for loading and processing class configuration options."""

    __SWITCH_KEY_SEPARATOR = "_#=_"
    __GLOBAL_CLASS_CONFIG_ATTRIBUTE = "GLOBAL_DYNCONFIG"

    SWITCH_DEFAULT = '_#!_SWITCH_DEFAULT'

    def __init__(self, global_config: SimpleNamespace, class_config: ClassConfigType, method_config: Optional[List],
                 assigned_class_config: Optional[Dict]):
        """
        Initialize a ClassConfigurationManager instance.

        :param global_config: The global configuration.
        :param class_config: The class configuration of the potential dependencies.
        :param method_config: The configuration of potential components passed from method decorators.
        :param assigned_class_config: The global configuration settings assigned using `set_configuration`.
        """
        self.__switches: Set = set()
        self.__default_switches: Set = set()
        self.class_importer = ClassImporter(global_config)
        self.__init_class_config(class_config, assigned_class_config)
        self.__init_global_config(global_config)
        self.__process_class_config(method_config)

    def __init_global_config(self, global_config: SimpleNamespace):
        """
        Initialize the global configuration using provided settings.

        :param global_config: The global configuration options.
        """
        self.global_conf = global_config
        if global_config_dict := self.class_conf.get(self.__GLOBAL_CLASS_CONFIG_ATTRIBUTE):
            self.set_default_global_config(self.global_conf, global_config_dict)

    def __init_class_config(self, class_config: Union[Dict, TypeClassOrPath], assigned_class_config: Optional[Dict]):
        """
        Initialize the class configuration for all the potential dependencies to be added using provided settings.

        :param class_config: The class configuration of the potential dependencies.
        :param assigned_class_config: The global configuration settings assigned using `set_configuration`.
        """
        if not isinstance(class_config, dict):
            class_config = class_to_dict(self.class_importer.get_imported_class(class_config))
            class_config.update(assigned_class_config or {})
        self.class_conf = defaultdict(list, class_config)

    def __process_class_config(self, method_config: Optional[List]):
        """
        Merge class and method configuration options, then sort the option selectors based on the provided order, if
        any.

        :param method_config: The component configuration passed from method decorators.
        """
        self.class_conf.pop(self.__GLOBAL_CLASS_CONFIG_ATTRIBUTE, None)
        self.class_conf = self.__transform_switches(self.class_conf)
        if method_config:
            self.__merge_method_config(method_config)
        if self.global_conf.option_order:
            self.option_selectors = sorted(
                self.class_conf.keys(),
                key=lambda i: self.global_conf.option_order.index(i)
            )
        else:
            self.option_selectors = list(self.class_conf.keys())

    @staticmethod
    def __is_switch_configuration(selector_node: Any) -> bool:
        """
        Check if a selector node represents a switch option configuration.

        :param selector_node: The selector node to check.
        :return: True if the node represents a switch option, False otherwise.
        """
        return isinstance(selector_node, Dict) and not isinstance(selector_node, ClassConfig)

    def __transform_switches(self, class_config: defaultdict) -> defaultdict:
        """
        Transform a switch configuration into a set of boolean configurations, where each configuration represents
        whether the corresponding option is selected or not.

        :param class_config: The input class configuration.
        :return: The transformed class configuration.
        """
        for key, values in class_config.copy().items():
            for value in tuplefy(values):
                if self.__is_switch_configuration(value):
                    for option_key, config in value.items():
                        if option_key == self.SWITCH_DEFAULT:
                            self.__default_switches.add(key)
                            class_config[key] = config
                        else:
                            class_config[self.__get_switch_key(key, option_key)] = config
                    if not isinstance(class_config[key], ClassConfig):
                        class_config.pop(key)
                    self.__switches.add(key)
        return class_config

    def __merge_method_config(self, method_config: List):
        """
        Merge the configuration passed from method decorators with the class configuration.

        :param method_config: The component configuration passed from method decorators.
        """
        for config_node in method_config:
            for key, values in self.__transform_switches(config_node.options).items():
                for value in tuplefy(values):
                    if value.component_class:
                        value.injection_method = config_node.method
                    try:
                        self.class_conf[key].append(value)
                    except AttributeError:
                        self.class_conf[key] = [self.class_conf[key], value]

    def __get_switch_key(self, key: str, option: Any) -> str:
        """
        Generate a switch key from a couple of switch key/option.

        :param key: The original key.
        :param option: The switch option.
        :return: The generated switch key.
        """
        return self.__SWITCH_KEY_SEPARATOR.join((key, str(option)))

    def get_default_class(self, class_config: Any) -> Optional[Type]:
        """
        Get the default class from the class configuration, if any.

        :param class_config: The class configuration.
        :return: The default class if any, None otherwise.
        """
        return (
            class_config.default_class or getattr(self.global_conf, "default_class", None)
            if isinstance(class_config, ClassConfig)
            else None
        )

    def transform_options(self, options: Dict):
        """
        Transform a switch option into a set of boolean options, so that they are compatible with the corresponding
        transformed switch configurations.

        :param options: The configuration options to process.
        """
        switches_to_add = {key for key in options.keys() if key in self.__switches}
        for key in switches_to_add:
            options[self.__get_switch_key(key, str(options[key]))] = True
            options.pop(key)
        for default_key in self.__default_switches:
            if default_key not in switches_to_add:
                options[default_key] = True

    def get_global_setting(self, dependent_class_conf: ClassConfig, key: str) -> Any:
        """
        Get a global setting for a dependent class.

        :param dependent_class_conf: The configuration of the dependent class.
        :param key: The setting's key.
        :return: The global setting value.
        """
        return getattr(dependent_class_conf, key, self.global_conf.__dict__[key])

    @staticmethod
    def set_default_global_config(global_config: SimpleNamespace, defaults: Optional[List]):
        """
        Set default non-empty values in a global configuration dictionary.

        :param global_config: The global configuration dictionary to set defaults in.
        :param defaults: The default values.
        """
        for key, value in defaults.__dict__.items():
            if value is not None:
                global_config.__dict__[key] = value

    @staticmethod
    def set_default_class_config(class_config: ClassConfig, defaults: SimpleNamespace):
        """
        Set default values in a class configuration if the corresponding keys do not exist.

        :param class_config: The class configuration to set defaults in.
        :param defaults: The default values.
        """
        for key, value in defaults.__dict__.items():
            if hasattr(class_config, key) and getattr(class_config, key) is None:
                setattr(class_config, key, value)
