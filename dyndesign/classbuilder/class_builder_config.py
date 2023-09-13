from dataclasses import dataclass
from typing import Dict, Optional, Type, Tuple, Union

from .class_importer import TypeClassOrPath
import dyndesign.exceptions as exc

__all__ = ["ClassConfig", "GlobalClassConfig"]


@dataclass
class BaseConfig:
    """
    A configuration class that defines settings shared by both global and class configurations.
    """
    default_class: Optional[Type] = None
    component_attr: str = None  # type: ignore
    injection_method: Optional[str] = None
    add_components_after_method: Optional[bool] = None
    structured_component_type: Optional[Type] = None
    structured_component_key: Optional[str] = None
    init_args_from_self: Union[Tuple[str, ...], str, None] = None
    init_kwargs_from_self: Optional[Dict] = None
    init_args_keep_first: Optional[int] = None
    strict_missing_args: Optional[bool] = None


@dataclass
class GlobalClassConfig(BaseConfig):
    """
    A configuration class that defines the global configuration to be used when building a class.
    """
    build_recursively: Optional[bool] = None
    class_builder_base_dir: Optional[str] = None
    option_order: Optional[Tuple[str, ...]] = None


@dataclass
class ClassConfig(BaseConfig):
    """
    A configuration class that defines the configuration of the class dependencies to be used when a specific condition
    is met.
    """
    inherit_from: Union[Tuple[TypeClassOrPath, ...], TypeClassOrPath, None] = None
    component_class: Optional[TypeClassOrPath] = None
    __is_option_selected: Optional[bool] = None  # type: ignore

    @property
    def is_option_selected(self):
        return self.__is_option_selected

    @is_option_selected.setter
    def is_option_selected(self, value):
        self.__is_option_selected = value

    def __post_init__(self):
        """Validate the class configuration."""
        if not self.inherit_from and not self.component_class:
            raise exc.ClassConfigMissingDependency(
                "ClassConfig configurator must include either one of the following fields: 'inherit_from' and "
                "'component_class'"
            )
        if self.inherit_from and self.component_class:
            raise exc.ClassConfigDependencyOverflow(
                "ClassConfig configurator must include only one of the following fields: 'inherit_from' and "
                "'component_class'"
            )
