from collections import defaultdict
from enum import IntEnum, auto
from typing import Any, Callable, Dict, List, Set, Tuple, Type, Union

from .dependency_configuration import DependencyConfiguration
from .class_configuration_manager import ClassConfigurationManager, DependencyKeyType
import dyndesign.exceptions as exc
from dyndesign.dyninherit.dyninherit_base import safesuper
from dyndesign.utils.inspector import is_invoking_method_in_one_line, is_method_not_defined_in_class
from dyndesign.utils.misc import tuplefy, invoke_first_method
from dyndesign.utils.signature import call_obj_with_adapted_args


class InjectionPosition(IntEnum):
    """Possible locations within the method's body where a component can be injected."""
    BEFORE = auto()
    MIDDLE = auto()
    AFTER = auto()


class ComponentClassBuilder:
    """ComponentClassBuilder is responsible for injecting component classes into a base class."""

    __COMPONENTS_APPLIED: Set = set()
    __EXPLICIT_METHOD_INJECTION: Dict = {}

    def __init__(self, base_class: Type, config_manager: ClassConfigurationManager,
                 configure_dependent_class_callback: Callable):
        """
        Initialize the ComponentClassBuilder instance.

        :param base_class: The base class to which components will be applied.
        :param config_manager: An instance of ClassConfigurationManager for loading configuration.
        :param configure_dependent_class_callback: A callback invoked to recursively configure the component classes.
        """
        self.__COMPONENTS_APPLIED = set()
        self.__args: Tuple = ()
        self.__kwargs: Dict = {}
        self.__base_class = base_class
        self.__config_manager = config_manager
        self.__configure_dependent_class = configure_dependent_class_callback
        self.__methods_to_patch: defaultdict = defaultdict(list)
        self.patched_methods: Dict = {}

    def __set_arguments(self, args: Tuple, kwargs: Dict):
        """
        Set the positional and keyword arguments to be used to initialize the component classes.

        :param args: Positional arguments used to initialize the component classes.
        :param kwargs: Keyword arguments used to initialize the component classes.
        """
        self.__args = args
        self.__kwargs = kwargs

    def __init_component(self, obj: object, component_config: DependencyConfiguration) -> Union[Callable, None]:
        """
        Create a component instance by modifying the arguments of the injection method that are passed to the
        component's __init__ method, based on the given configuration. The component class is also configured so that
        all its potential dependent classes are recursively configured.

        :param obj: The object to which the component will be added.
        :param component_config: The configuration of the component to be instantiated.
        :return: The component instance if the component is instantiated, None otherwise.
        """
        add_args = list(self.__args)
        add_kwargs = {}
        if component_config.init_args_keep_first:
            add_args = add_args[0:component_config.init_args_keep_first]
        if component_config.init_args_from_option:
            add_args.insert(0, component_config.selected_option)
        if component_config.init_args_from_self:
            for arg_name in tuplefy(component_config.init_args_from_self):
                if hasattr(obj, arg_name):
                    add_args.append(getattr(obj, arg_name))
        if component_config.init_kwargs_from_self:
            for kwarg_key, kwarg_name in component_config.init_kwargs_from_self.items():
                if hasattr(obj, kwarg_name):
                    add_kwargs[kwarg_key] = getattr(obj, kwarg_name)
        component_class = (
            component_config.component_class if component_config.must_be_added
            else self.__config_manager.get_default_class(component_config)
        )
        return call_obj_with_adapted_args(
            self.__configure_dependent_class(component_class),
            None,
            *add_args,
            strict_missing_args=bool(component_config.strict_missing_args),
            **add_kwargs, **self.__kwargs
        )

    def __is_the_right_injection_position(self, component_config: DependencyConfiguration,
                                          position: InjectionPosition) -> bool:
        """
        Determine if the component must be injected in the given position based on the configuration or not.

        :param component_config: The component configuration.
        :param position: The injection position.
        :return: True if the injection is in the right position, False otherwise.
        """
        return (
            position == InjectionPosition.MIDDLE
            or (
                (position == InjectionPosition.BEFORE)
                ^ bool(self.__config_manager.get_global_setting(component_config, 'add_components_after_method'))
            )
        )

    def __is_component_already_applied(self, component_config: DependencyConfiguration, method: str) -> bool:
        """
        Check whether the component configuration has been already applied or not.

        :param component_config: The component configuration.
        :param method: The method name.
        :return: True if the component has been applied, False otherwise.
        """
        return (component_config.component_class, method, component_config.component_attr) in self.__COMPONENTS_APPLIED

    def __is_component_to_inject(self, component_config: DependencyConfiguration, position: InjectionPosition,
                                 method: str) -> bool:
        """
        Check whether the component must be injected or not.

        :param component_config: The component configuration.
        :param position: The injection position.
        :param method: The method name.
        :return: True if the component must be injected, False otherwise.
        """
        return bool(
            self.__is_the_right_injection_position(component_config, position)
            and component_config.injection_method and method == component_config.injection_method
            and not self.__is_component_already_applied(component_config, method)
        )

    @staticmethod
    def __add_instance_to_structure(struct_component, method_names, *args):
        try:
            invoke_first_method(struct_component, method_names, *args)
        except exc.NoMethodFound:
            raise exc.StructuredTypeError("Error instantiating `structured_component_type`")

    def __init_structured_component(self, component_instance: Callable, obj: object,
                                    component_config: DependencyConfiguration) -> Any:
        """
        If `structured_component_type` global setting is specified, return an object of that type containing the
        component instance.

        :param component_instance: The component instance to be added.
        :param obj: The object to which the component will be added.
        :param component_config: The component configuration.
        :return: An object of type `structured_component_type` if that setting is specified, `component_instance`
                 otherwise.
        """
        if structured_component_type := self.__config_manager.get_global_setting(component_config,
                                                                                 'structured_component_type'):
            struct_component = getattr(obj, component_config.component_attr, None)
            if not struct_component:
                struct_component = structured_component_type()
            if component_config.structured_component_key:
                self.__add_instance_to_structure(struct_component, ('__setitem__', '__setattr__'),
                                                 component_config.structured_component_key, component_instance)
            else:
                self.__add_instance_to_structure(struct_component, ('append', 'add'), component_instance)
            return struct_component
        return component_instance

    def __add_component(self, component_config: DependencyConfiguration, obj: object, method: str,
                        position: InjectionPosition):
        """
        Add a component to the object based on the component configuration.

        :param component_config: The component configuration.
        :param obj: The object to which the components are being added.
        :param method: The method to which the components are being added.
        :param position: The injection position.
        """
        if (
                self.__is_component_to_inject(component_config, position, method)
                and (component_instance := self.__init_component(obj, component_config))
        ):
            component_instance = self.__init_structured_component(component_instance, obj, component_config)
            setattr(obj, component_config.component_attr, component_instance)
            self.__COMPONENTS_APPLIED.add(
                (component_config.component_class, method, component_config.component_attr)
            )

    def __add_key_components(self, dependency_keys: List[str], obj: object, method: str, position: InjectionPosition):
        """
        Add the components selected through the dependency_keys to the object based on configuration.

        :param dependency_keys: The list of component dependency keys.
        :param obj: The object to which the components are being added.
        :param method: The method to which the components are being added.
        :param position: The injection position.
        """
        for dependency_key in dependency_keys:
            for config_unit in self.__config_manager.class_configs:
                for component_config in tuplefy(config_unit.dependencies[dependency_key]):
                    self.__add_component(component_config, obj, method, position=position)

    def __invoke_injection_method(self, method: str, obj: object) -> Any:
        """
        Invoke the injection method with adapted arguments. The arguments of the injection method may need to be
        modified to include additional or different arguments that are required by the component's __init__ constructor.

        :param method: The method name.
        :param obj: The object on which the method is invoked.
        :return: The result of the method invocation.
        """
        injection_method = getattr(self.__base_class, method)
        if injection_method:
            if is_method_not_defined_in_class(injection_method):
                # If the class inherits from a parent class, call the injection method from the parent class.
                if len(obj.__class__.__bases__) > 1:
                    injection_method = safesuper(obj.__class__.__base__, obj).__init__  # type: ignore
                    # In this case, the method needs to be called without passing `obj` as first argument.
                    obj = None
                else:
                    return None
            return call_obj_with_adapted_args(injection_method, obj, *self.__args, strict_missing_args=True,
                                              **self.__kwargs)
        return None

    def __has_components_explicitly_injected(self, dependency_keys: List[str], method: str) -> bool:
        """
        If a method has a call to the component injector, record it to be processed in `explicitly_inject_components`.

        :param dependency_keys: The list of component dependency keys.
        :param method: The method name.
        :return: True if the method has a call to the component injector, False otherwise.
        """
        method_instance = getattr(self.__base_class, method)
        if is_invoking_method_in_one_line(method_instance, "dynconfig.inject_components"):
            self.__EXPLICIT_METHOD_INJECTION[method] = dependency_keys
            self.patched_methods[method] = method_instance
            return True
        return False

    def __patch_method(self, dependency_keys: List[str], method: str) -> None:
        """
        Patch a method by injecting components before or after its execution.

        :param dependency_keys: The list of dependency keys related to the components to be injected.
        :param method: The method name.
        """
        if self.__has_components_explicitly_injected(dependency_keys, method):
            return

        def patched_method(obj: object, *args, **kwargs) -> Any:
            """
            This method is responsible for adding injected components to a method. It injects the components before
            or after invoking the original method and handles the adaptation of arguments.

            :param obj: The object on which the method is invoked.
            :param args: Positional arguments used to initialize the component class and to pass to the injection
                         method.
            :param kwargs: Keyword arguments used to initialize the component class and to pass to the injection method.
            :return: The result of the method invocation.
            """
            self.__set_arguments(args, kwargs)
            self.__add_key_components(dependency_keys, obj, method, position=InjectionPosition.BEFORE)
            returned_value = self.__invoke_injection_method(method, obj)
            self.__add_key_components(dependency_keys, obj, method, position=InjectionPosition.AFTER)
            return returned_value

        self.patched_methods[method] = patched_method

    def select_component_class(self, dependency_key: DependencyKeyType, component_config: DependencyConfiguration):
        """
        Select the component classes to be injected based on the configuration.

        :param dependency_key: The key of the component class to be added.
        :param component_config: The configuration of the component class.
        """
        component_config.set_default_class_config(self.__config_manager.global_conf)
        component_config.validate_component_configuration(self.__base_class)
        self.__methods_to_patch[component_config.injection_method].append(dependency_key)

    def inject_components_before_or_after_methods(self):
        """
        Inject component classes before or after corresponding methods based on the configuration.
        """
        for method, dependency_keys in self.__methods_to_patch.items():
            self.__patch_method(dependency_keys, method)

    def explicitly_inject_components(self, obj: object, method: str, *args, **kwargs):
        """
        Inject components from an explicit injection point within a method based on the configuration, as opposed to
        implicitly injecting them either before or after the method.

        :param obj: The object on which the method is invoked.
        :param method: The method name.
        :param args: Positional arguments used to initialize the component class.
        :param kwargs: Keyword arguments used to initialize the component class.
        """
        dependency_keys = self.__EXPLICIT_METHOD_INJECTION[method]
        self.__set_arguments(args, kwargs)
        self.__add_key_components(dependency_keys, obj, method, position=InjectionPosition.MIDDLE)
