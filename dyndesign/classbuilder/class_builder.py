from typing import Any, Dict, Type

from .dependency_configuration import DependencyConfiguration
from .class_configuration_manager import ClassConfigurationManager, DependencyKeyType
from .class_importer import TypeClassOrPath
from .class_storage import ClassStorage
from .parent_class_builder import ParentClassBuilder
from .component_class_builder import ComponentClassBuilder
from dyndesign.utils.inspector import get_arguments
from dyndesign.exceptions import ClassConfigMissingDependency


class ClassBuilder:
    """
    Class Builder utilized to create a built class by applying the options selected from a class configuration settings
    to a base class.
    """

    def __init__(self, base_class: Type, config_manager: ClassConfigurationManager):
        """
        Initialize a ClassBuilder instance.

        :param base_class: The base class upon which to build the new class.
        :param config_manager: An instance of ClassConfigurationManager for loading class configuration.
        """
        self.__base_class = base_class
        self.__config_manager = config_manager

    def __get_option_value(self, dependency_key: DependencyKeyType) -> Any:
        """
        Return the value of the configuration option for a dependency key.

        :param dependency_key: The configuration dependency key.
        :return: The value of the configuration option corresponding to the key.
        """
        if isinstance(dependency_key, (staticmethod, classmethod)):
            dependency_key = dependency_key.__func__
        if callable(dependency_key):
            func_args = get_arguments(dependency_key).args
            args = (self.__CLASS_OPTIONS.get(f_arg, getattr(self.__base_class, f_arg, None)) for f_arg in func_args)
            return dependency_key(*args)
        else:
            return self.__CLASS_OPTIONS.get(dependency_key)

    def __configure_dependent_class(self, dependent_class: TypeClassOrPath) -> Type:
        """
        Recursively configure a dependent class based on the class options.

        :param dependent_class: The dependent class or path to dependent class to be configured.
        :return: The built class.
        """
        dependent_class = self.__config_manager.class_importer.get_imported_class(dependent_class)
        if (not self.__config_manager.global_conf.build_recursively
                or dependent_class == self.__base_class
                or ClassStorage.is_already_built(dependent_class)):
            return dependent_class
        return ClassStorage.config_map[dependent_class].configure_class(self.__CLASS_OPTIONS)

    def __setup_class_configuration(self, options: Dict):
        """
        Set up the configuration for building a class.

        :param options: The configuration options.
        """
        self.__CLASS_OPTIONS = options
        self.__parent_class_builder = ParentClassBuilder(self.__base_class, self.__configure_dependent_class)
        self.__component_class_builder = ComponentClassBuilder(
            self.__base_class,
            self.__config_manager,
            self.__configure_dependent_class
        )

    def __prepare_class_dependency(self, dependency_key: DependencyKeyType, dependency_config: DependencyConfiguration):
        """
        Prepare a dependent classes to be added to the base class based on the class configuration and whether the
        corresponding configuration option is selected or not.

        :param dependency_key: The key corresponding to the component to be potentially added.
        :param dependency_config: The class configuration of the dependent class to be added.
        """
        default_class = self.__config_manager.get_default_class(dependency_config)
        if dependency_config.must_be_added or default_class:
            if dependency_config.inherit_from:
                parent_class = dependency_config.inherit_from if dependency_config.must_be_added else default_class
                self.__parent_class_builder.select_parent_classes(parent_class)
            elif dependency_config.component_class:
                self.__component_class_builder.select_component_class(dependency_key, dependency_config)
            else:
                # This is a fallback in case the `ClassConfigMissingDependency` exception is not raised when validating
                # the `ClassConfig` object.
                raise ClassConfigMissingDependency

    def __prepare_class_dependencies(self):
        """
        Prepare the dependent classes to be added to the base class based on the selected options.
        """
        for config_unit in self.__config_manager.class_configs:
            self.__config_manager.set_default_global_config(config_unit)
            for dependency_key in config_unit.dependency_keys:
                selected_option = self.__get_option_value(dependency_key)
                for dependency_config in config_unit.get_dependencies(dependency_key):
                    dependency_config.setup(
                        selected_option,
                        self.__config_manager.get_default_global_config(dependency_config, "force_add")
                    )
                    self.__prepare_class_dependency(dependency_key, dependency_config)

    def configure_class(self, options: Dict) -> Type:
        """
        Build a class using the selected configuration options, and then configure any dependent classes recursively.

        :param options: The configuration options.
        :return: The built class.
        """
        self.__setup_class_configuration(options)
        self.__prepare_class_dependencies()
        self.__parent_class_builder.configure_parent_classes()
        self.__component_class_builder.inject_components_before_or_after_methods()
        return type(
            self.__base_class.__name__,
            self.__parent_class_builder.parent_classes_configured,
            self.__component_class_builder.patched_methods
        )

    def build_configured_class(self, options: Dict) -> Type:
        """
        Build a class based on the options selected from the class configuration.

        :param options: The selected options.
        :return: The built class.
        """
        self.__config_manager.transform_options(options)
        return self.configure_class(options)

    def inject_components_into_method(self, obj: object, method: str, *args, **kwargs):
        """
        Inject components into a method of the given object based on the selected configuration.

        :param obj: The object on which the method is invoked.
        :param method: The method name.
        :param args: Positional arguments used to initialize the component class.
        :param kwargs: Keyword arguments used to initialize the component class.
        """
        self.__component_class_builder.explicitly_inject_components(obj, method, *args, **kwargs)
